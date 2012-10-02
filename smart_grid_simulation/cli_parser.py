import sys
import argparse

from smart_grid_simulation.simulation import (
    Actor, RemoteActor, ControllerActor)

import urlparse

def check_uri(uri):
    parsed = urlparse.urlparse(uri)
    if not parsed.scheme in ["http", "https"]:
        raise argparse.ArgumentTypeError(
            "%r is not a valid URL. scheme must be http(s)!" % uri)

    # cut off fragment
    uri = urlparse.urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                               parsed.params, parsed.query, ""))
    return uri


def get_actor_server_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--host-name', action="store",
        default='localhost',
        type=str, help=("Hostname/IP address to bind the "
            "server socket to. Default: 'localhost'"))
    parser.add_argument('-p', '--port', type=int,
        help=("Port to bind the "
             "server socket to. Default: 9001"),
        default=9001)

    subparsers = parser.add_subparsers(
        help=("Please decide: 'a' to start an Actor server, "
              "'r' to start a Controller Actor server."))

    actor_server = subparsers.add_parser('a',
        help='Start Actor server')
    actor_server.add_argument('-v', '--value',
        action='store', type=int,
        help=("Energy consumption value for actor. "
              "Integer, positive or negative"))
    actor_server.add_argument('--value-range', nargs='+', type=int,
        help=("Acceptable values for energy consumption "
              "of this actor server"),
        required=True)

    def actor_server_parse_args(args):
        host_port_tuple = args.host_name, args.port
        actor = Actor(
            value=args.value,
            value_range=args.value_range
        )
        return dict(host_port_tuple=host_port_tuple, actor=actor)
    actor_server.set_defaults(func=actor_server_parse_args)
    actor_server.set_defaults(case="actor_server")

    actor_controller = subparsers.add_parser('c',
         help='Start Controller Actor server')

    actor_controller.add_argument('-a', '--actor-uris', nargs='+',
        type=check_uri, required=True,
        help="URIs for remote actors of this controller actor actor"
    )

    csp_not_installed_msg = ("csp_solver not installed! "
        "To start Controller Actors install csp_solver from "
        "http://github.com/dmr/csp-solver.git")
    try:
        # The following arguments are not pretty here. They belong to
        # the CSP configuration but are needed if an actor_controller
        # is started
        # Easy defaults: current folder. Will fail if files don't exist
        import csp_solver
        actor_controller = csp_solver.add_csp_config_params_to_argparse_parser(
            actor_controller)
    except ImportError:
        print "Warning:", csp_not_installed_msg
        # will fail hard in actor_controller_parse_args

    def actor_controller_parse_args(args):
        try:
            import csp_solver
        except ImportError:
            print "!!! Error:", csp_not_installed_msg
            import sys
            sys.exit(1)

        csp_solver_config = csp_solver.get_valid_csp_solver_config(
            minisat_path=args.minisat,
            sugarjar_path=args.sugar_jar,
            tmp_folder=args.tmp_folder
        )

        actors=[RemoteActor(actor_uri)
                for actor_uri in args.actor_uris]
        actor = ControllerActor(
            actors=actors,
            csp_solver_config=csp_solver_config
        )
        host_port_tuple = args.host_name, args.port
        return dict(host_port_tuple=host_port_tuple, actor=actor)
    actor_controller.set_defaults(func=actor_controller_parse_args)

    return parser


def parse_actor_server_arguments(sys_args=sys.argv[1:],
         check_remote_actors=True # introduced to make this testable
                                 ):
    parser = get_actor_server_parser()
    parsed_args = parser.parse_args(args=sys_args)
    result = parsed_args.func(parsed_args)

    if check_remote_actors == True:
        # test is actors exist to prevent errors later
        if isinstance(result['actor'], ControllerActor):
            for actor in result['actor']._actors:
                import urllib2
                try:
                    actor.get_value()
                except urllib2.URLError as exc:
                    print exc.reason
                    import sys
                    sys.exit(1)

    return result

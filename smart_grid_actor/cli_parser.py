import sys
import argparse

from smart_grid_actor.actor import (
    Actor, RemoteActor, ControllerActor)

import urlparse
from smart_grid_actor.server import start_actor_server, CustomPool


def check_uri(uri):
    parsed = urlparse.urlparse(uri)
    if not parsed.scheme in ["http", "https"]:
        raise argparse.ArgumentTypeError(
            "%r is not a valid URL. scheme must be http(s)!" % uri)

    # cut off fragment
    uri = urlparse.urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                               parsed.params, parsed.query, ""))
    return uri


def get_parser():
    parser = argparse.ArgumentParser(
        "smart_grid_actor",
        description=(
            "Starts a Smart Grid Actor. This actor can "
            "either be a direct actor or a remote actor"
        )
    )

    parser.add_argument('--host-name', action="store",
        default='localhost',
        type=str, help=("Hostname/IP address to bind the "
            "server socket to. Default: '127.0.0.1'"))
    parser.add_argument('-p', '--port', type=int,
        help=("Port to bind the "
             "server socket to. Default: 9001"),
        default=9001)

    parser.add_argument('--log-requests', action="store_true",
        help=("Logs requests to std_err. Influences server speed negatively!")
    )

    parser.add_argument('--dry-run', action="store_true",
        help=("Don't do anything, just print parsed parameters"))

    subparsers = parser.add_subparsers(
        help=("Please decide: 'a' to start an Actor server, "
              "'r' to start a Controller Actor server."))
    add_actor_server_to_subparsers(subparsers)
    add_controller_actor_to_subparsers(subparsers)

    return parser


def start_the_actor_server(
        host_name,
        port,
        value_range,
        value,
        log_requests,
        dry_run=False
        ):
    actor = Actor(
        value=value,
        value_range=value_range
    )
    print "Actor: value_range={0}, value={1}".format(
        list(actor.get_value_range()), actor.get_value()
    )

    kw = dict(
        host_port_tuple=(host_name, port),
        actor=actor,
        log_to_std_err=log_requests
    )
    if dry_run:
        print "Would start an actor server on {0} but this is a test run".format(kw)
        return
    start_actor_server(**kw)


def add_actor_server_to_subparsers(subparsers):
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

    actor_server.set_defaults(execute_function=start_the_actor_server)


csp_not_installed_msg = (
    "csp_solver not installed! "
    "To start Controller Actors install csp_solver from "
    "http://github.com/dmr/csp-solver.git")


def start_controller_actor(
        host_name,
        port,
        minisat,
        sugar_jar,
        tmp_folder,
        actor_uris,
        log_requests,
        check_actor_uris,
        worker_count=None,
        dry_run=False,
        ):
    try:
        import csp_solver
    except ImportError:
        print "!!! Error:", csp_not_installed_msg
        import sys
        sys.exit(1)

    csp_solver_config = csp_solver.get_valid_csp_solver_config(
        minisat_path=minisat,
        sugarjar_path=sugar_jar,
        tmp_folder=tmp_folder
    )

    actors=[RemoteActor(actor_uri)
            for actor_uri in actor_uris]

    pool_kwargs = {}
    if worker_count:
        pool_kwargs['processes'] = worker_count
    pool = CustomPool(**pool_kwargs)

    actor = ControllerActor(
        actors=actors,
        csp_solver_config=csp_solver_config,
        multiprocessing_pool=pool
    )

    if check_actor_uris:
        # test is actors of a ControllerActor exist
        # to prevent errors later
        for actor in actor._actors:
            import urllib2
            try:
                actor.get_value()
            except urllib2.URLError as exc:
                print "Error while checking {0}: {1}".format(actor, exc.reason)
                import sys
                sys.exit(1)

    kw = dict(
        host_port_tuple=(host_name, port),
        actor=actor,
        log_to_std_err=log_requests
    )
    if dry_run:
        print "Would start an actor server on {0} but this is a test run".format(kw)
        return

    try:
        start_actor_server(**kw)
    except KeyboardInterrupt:
        print 'got ^C while pool mapping, terminating the pool'
        pool.terminate()
        print 'pool is terminated'
    except Exception, e:
        print 'got exception: %r, terminating the pool' % (e,)
        pool.terminate()
        print 'pool is terminated'
    finally:
        print 'joining pool processes'
        pool.join()
        print 'join complete'
    print 'the end'


def add_controller_actor_to_subparsers(subparsers):
    actor_controller = subparsers.add_parser('c',
        help='Start Controller Actor server')

    actor_controller.add_argument('-a', '--actor-uris', nargs='+',
        type=check_uri, required=True,
        help="URIs for remote actors of this controller actor actor"
    )

    actor_controller.add_argument('--check-actor-uris',
        action="store_true", default=False,
        help="Skips to check actor URIs for existence"
    )

    actor_controller.add_argument('--worker-count',
        help=(
            "Worker count for the parallel processing module. "
            "Defaults to CPU cores count"
        )
    )

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

    actor_controller.set_defaults(
        execute_function=start_controller_actor
    )

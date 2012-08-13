import sys
import argparse

from smart_grid_simulation.simulation import Actor, RemoteActor


def get_actor_server_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--host-name', action="store", default='localhost',
                        type=str, help="First server's port")
    parser.add_argument('-p', dest='port', type=int, help="Port for server",
                        default=9001)

    subparsers = parser.add_subparsers(
        help=("please decide: 'a' for actor server mode, "
              "'r' for actor controller, "
              "or 'server_starter' to start many servers?"))

    actor_server = subparsers.add_parser('a', help='Start actor server')
    actor_server.add_argument('-v', dest='value',
          action='store', type=int, default=0,
          help=("Energy consumption alue for actor. "
                "Integer, positive or negative"))
    actor_server.add_argument('--value-range', action='append',
          help=("Acceptable values for energy consumption "
                "of this actor server"))
    def actor_server_parse_args(args):
        host_port_tuple = args.host_name, args.port

        if args.value_range:
            value_range = [int(v) for v in args.value_range]
            assert args.value in value_range,\
            'please choose value from value_range'
            print value_range
        else:
            value_range = [args.value]

        actor = Actor(
            value=args.value,
            value_range=value_range
        )
        return dict(host_port_tuple=host_port_tuple, actor=actor)
    actor_server.set_defaults(func=actor_server_parse_args)


    actor_server.set_defaults(case="actor_server")


    actor_controller = subparsers.add_parser('c',
         help='Start actor as controller actor server')
    actor_controller.add_argument('-a', dest='actor_uris', action='append',
          help="URIs for remote actors of this controller actor actor"
          # TODO: validate that uri is valid, check if available?
    )
    # TODO: -v?
    def actor_controller_parse_args(args):
        host_port_tuple = args.host_name, args.port

        actors=[RemoteActor(actor_uri)
                for actor_uri in args.actor_uris]

        # test is actors exist?
        for a in actors:
            a.get_value()

        actor = ControllerActor(
            host_port_tuple=host_port_tuple,
            actors=actors
        )
        return dict(host_port_tuple=host_port_tuple, actor=actor)
    actor_controller.set_defaults(func=actor_controller_parse_args)
    return parser


def parse_actor_server_arguments(sys_args=sys.argv[1:]):
    args = get_actor_server_parser().parse_args(args=sys_args)
    return args.func(args)

cd



def parse_actor_server_starter_arguments(sys_args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--host-name', action="store", default='localhost',
                        type=str, help="First server's port")

    parser.add_argument('-s','--start_port', action="store", default=9000,
                        type=int, help="First server's port")
    parser.add_argument('-e', '--exclude', action="append",
                        type=int, help='Exclude ports')

    parser.add_argument('-n','--number', action="store", default=4496,
                        type=int, help='Start n servers')


    #import resource
    #resource.setrlimit(resource.RLIMIT_NOFILE, (10000,-1))
    #print 'getrlimit', resource.getrlimit(resource.RLIMIT_NOFILE)
    #parser.add_argument('-b','--branching-factor', action="store", type=int)
    #parser.add_argument('-d','--hierarchy-depth', action="store", type=int)

    #actor_count = 256
    #contr_start_port = 10000
    #c_all_port = 9998
    #c_of_cs_port = 9997
    #actors_per_controller = 4

    #if argparse_results.branching_factor or argparse_results.hierarchy_depth:
    #    assert 0, 'please implement first.'


    argparse_results = parser.parse_args(args=sys_args)

    port_range = range(argparse_results.start_port,
                       argparse_results.start_port+argparse_results.number)
    if argparse_results.exclude:
        for exclude_port in argparse_results.exclude:
            if exclude_port in port_range:
                port_range.append(max(port_range)+1)
                port_range.remove(exclude_port)
        print "Starting {0} servers: {1} --> {2}. excluded {3}".format(
            len(port_range), min(port_range), max(port_range),
            ', '.join(str(e) for e in argparse_results.exclude))
    else:
        print "Starting {0} servers: {1} --> {2}".format(
            len(port_range),min(port_range),max(port_range))


    res = []

    for i, port in enumerate(port_range):
        host_port_tuple = host_name, port
        actor = Actor(
            # TODO: random?
            value=2,
            value_range=[0,2,1]
        )
        res.append((host_port_tuple, actor))

    return res
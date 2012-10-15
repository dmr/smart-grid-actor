import argparse

from smart_grid_actor.actor import Actor
from smart_grid_actor.server import start_actor_server, CustomPool


def add_actor_base_parser_params(parser):
    parser.add_argument('--host-name', action="store",
        default='localhost',
        type=str, help=("Hostname/IP address to bind the "
            "server socket to. Default: '127.0.0.1'"))
    parser.add_argument('-p', '--port', type=int,
        help=("Port to bind the "
             "server socket to. Default: 9001"),
        default=9001)

    parser.add_argument('--log-requests', action="store_true",
        help=("Logs requests to std_err (Slow)")
    )

    parser.add_argument('--dry-run', action="store_true",
        help=("Don't do anything, just print parsed parameters"))


def get_parser():
    parser = argparse.ArgumentParser(
        "smart_grid_actor",
        description=(
            "Starts a Smart Grid Actor."
        )
    )
    add_actor_base_parser_params(parser)
    add_actor_server_params(parser)
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
        return kw
    start_actor_server(**kw)


def add_actor_server_params(parser):
    parser.add_argument('-v', '--value',
        action='store', type=int,
        help=("Energy consumption value for actor. "
              "Integer, positive or negative"))
    parser.add_argument('--value-range', nargs='+', type=int,
        help=("Acceptable values for energy consumption "
              "of this actor server"),
        required=True)

    parser.set_defaults(execute_function=start_the_actor_server)

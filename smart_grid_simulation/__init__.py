#!/usr/bin/env python
import sys

from smart_grid_simulation.server import start_actor_server
from smart_grid_simulation.cli_parser import get_parser
from smart_grid_simulation.simulation import ControllerActor


def parse_arguments(
        sys_args=sys.argv[1:],
        check_remote_actors=True
        ):
    parser = get_parser()
    parsed_args = parser.parse_args(args=sys_args)
    result = parsed_args.func(parsed_args)

    if check_remote_actors == True:
        # test is actors of a ControllerActor exist
        # to prevent errors later
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


def main():
    arguments = parse_arguments()
    _port, _process = start_actor_server(**arguments)

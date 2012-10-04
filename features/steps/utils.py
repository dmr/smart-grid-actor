import smart_grid_simulation
from smart_grid_simulation.server import start_actor_server
from smart_grid_simulation.cli_parser import parse_actor_server_arguments

def add_actor_server_to_context(context, port, vr=None, actors=None):
    assert vr or actors

    args = "-p={0} ".format(port)

    if vr:
        assert isinstance(vr, list)
        args += 'a --value-range {0}'.format(
            " ".join([str(v) for v in vr])
        )

    if actors:
        assert isinstance(actors, list)
        args += 'c -a {0}'.format(
            " ".join(str(v) for v in actors)
        )
        import os
        args += ' --sugar-jar={0}'.format(
            os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                '../../tests/sugar-v1-15-0.jar'
            )),
        )

    sys_args = args.split()
    parsed_args = parse_actor_server_arguments(sys_args=sys_args)
    _port, actor_server_process = start_actor_server(
        start_in_background_thread=True,
        **parsed_args
    )

    # context.servers: all servers will be
    # stopped in environment.py
    if hasattr(context, 'servers'):
        context.servers.append(actor_server_process)
    else:
        context.servers = [actor_server_process]

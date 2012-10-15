#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import argparse

from smart_grid_actor.server import start_actor_server
from smart_grid_actor.cli_parser import add_actor_server_params, create_actor

def save_to_file(file, content, force=False):
    if force:
        if os.path.exists(file):
            print "Overwriting file '{0}'".format(file)
    elif os.path.exists(file):
        resp = ''
        while resp.lower() not in ['yes', 'no']:
            resp = raw_input("\n>>> Do you want to overwrite the file '{0}'? (yes/no)\n".format(
                file))
        if resp.lower() != "yes":
            print "Not saving to '{0}'".format(file)
            return
    with open(file, 'wb') as fp:
        fp.write(content)


def start_actor_servers(
        number,
        host_name,
        value_range,
        value=None,
        start_port=None,
        exclude_ports=None,
        save_to_json=None,
        force=False,
        stop_servers_after_json_save=False # for testing
        ):

    if start_port:
        port_range = range(start_port,
            start_port+number)

        if exclude_ports:
            for exclude_port in exclude_ports:
                if exclude_port in port_range:
                    port_range.append(max(port_range)+1)
                    port_range.remove(exclude_port)
            print "Starting {0} servers: {1} --> {2}. excluded {3}".format(
                len(port_range), min(port_range), max(port_range),
                ', '.join(str(e) for e in exclude_ports))
        else:
            print "Starting {0} servers: {1} --> {2}".format(
                len(port_range),min(port_range),max(port_range))

        servers_to_start = []
        for i, port in enumerate(port_range):
            servers_to_start.append(dict(
                host_port_tuple=(host_name, port),
                actor=create_actor(value_range=value_range, value=value)
            ))

    else:
        servers_to_start = [
            dict(
                actor=create_actor(value_range=value_range, value=value)
            )
            for _ in range(number)
        ]

    started_servers = []
    for kw in servers_to_start:
        port, process = start_actor_server(
            start_in_background_thread=True,
            **kw
        )
        started_servers.append((port, process))

    print "{0} servers started".format(len(started_servers))

    if save_to_json:
        print "Saving used ports to file '{0}'".format(save_to_json)
        json_content = json.dumps([port for port, _process in started_servers])
        save_to_file(save_to_json, json_content, force=force)

    if stop_servers_after_json_save:
        for _port, process in started_servers:
            process.terminate()
        return started_servers

    try:
        print "I am done starting. Now waiting for KeyboardInterrupt or SystemExit."
        import time
        while True:
            time.sleep(600)
    except (KeyboardInterrupt, SystemExit):
        print "Exiting..."


def get_batch_starter_parser():
    parser = argparse.ArgumentParser()

    add_actor_server_params(parser)

    parser.add_argument('--host-name', action="store", default='localhost',
        type=str, help="Interface to bind the started servers to")

    parser.add_argument('-n','--number', action="store",
        type=int, help='Start n servers',
        required=True
    )

    parser.add_argument('-s','--start-port', action="store",
        type=int, help="First server's port")
    parser.add_argument('-e', '--exclude-ports', nargs='+',
        type=int, help='Exclude ports')

    parser.add_argument('--save-to-json', action="store",
        type=unicode, help=(
            'Save ports of started servers to a json file.'
            )
    )
    parser.add_argument('--force', action="store_true",
        help=(
            'Overwrite a file at save-to-json without asking'
            )
    )

    parser.set_defaults(execute_function=start_actor_servers)
    return parser


def main():
    parser = get_batch_starter_parser()
    parsed_args_dct = parser.parse_args().__dict__
    parsed_args_dct.pop('execute_function')(**parsed_args_dct)


if __name__ == '__main__': main()

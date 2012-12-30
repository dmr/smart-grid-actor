# -*- coding: utf-8 -*-
from __future__ import print_function
import json
import urllib2
import urlparse
import os

import argparse

from smart_grid_actor.server import start_actor_server
from smart_grid_actor.cli import add_actor_server_params, create_actor


def save_to_file(file_name, content, force=False):
    if force:
        if os.path.exists(file_name):
            print("Overwriting file '{0}'".format(file_name))
    elif os.path.exists(file_name):
        resp = ''
        while resp.lower() not in ['yes', 'no']:
            resp = raw_input("\n>>> Do you want to overwrite the"
                "file '{0}'? (yes/no)\n".format(file_name))
        if resp.lower() != "yes":
            print("Not saving to '{0}'".format(file_name))
            return
    with open(file_name, 'wb') as file_object:
        file_object.write(content)


def start_actor_servers(
        number,
        host_name,

        # actor params
        value_range,
        value=None,

        start_port=None,
        exclude_ports=None,
        save_to_json=None,
        callback_uri=None,
        force=False,
        stop_servers_after_json_save=False # for testing
        ):
    # handling of host_name is inconsistent: only used if
    # start_port is set.
    if start_port:
        port_range = range(start_port,
            start_port+number)

        if exclude_ports:
            for exclude_port in exclude_ports:
                if exclude_port in port_range:
                    port_range.append(max(port_range)+1)
                    port_range.remove(exclude_port)
            print("Starting {0} servers: {1} --> {2}. excluded {3}".format(
                len(port_range), min(port_range), max(port_range),
                ', '.join(str(e) for e in exclude_ports)))
        else:
            print("Starting {0} servers: {1} --> {2}".format(
                len(port_range),min(port_range),max(port_range)))

        servers_to_start = []
        for port in port_range:
            servers_to_start.append({
                'host_port_tuple':(host_name, port),
                'actor':create_actor(value_range=value_range, value=value)
            })

    else:
        servers_to_start = [
            {'actor':create_actor(value_range=value_range, value=value)}
            for _ in range(number)
        ]

    lst_of_started_servers = [
        # will respond with
        # (real_host_name, port), process
        start_actor_server(
            start_in_background_thread=True,
            **kw
        )
        for kw in servers_to_start
    ]

    print("{0} servers started".format(len(lst_of_started_servers)))

    lst_of_started_servers_uris = [
        uri for uri, _process in lst_of_started_servers
    ]

    if save_to_json:
        print("Saving used ports to file '{0}'".format(save_to_json))
        json_content = json.dumps(lst_of_started_servers_uris)
        save_to_file(save_to_json, json_content, force=force)

    if callback_uri:
        print("POST to callback URI '{0}': {1}".format(
            callback_uri,
            lst_of_started_servers_uris
        ))
        request = urllib2.Request(
            callback_uri,
            # a request containing "data" will be a POST request
            data=json.dumps(lst_of_started_servers_uris)
        )
        try:
            resp = urllib2.urlopen(request)
            if resp.code == 200:
                print("POST successful.")

        except urllib2.URLError as exc:
            print(exc)
            print("Error connecting to callback URI!")

    if stop_servers_after_json_save:
        for _, process in lst_of_started_servers:
            process.terminate()
        return lst_of_started_servers

    try:
        print("I am done starting. Now waiting for "
            "KeyboardInterrupt or SystemExit.")
        import time
        while True:
            time.sleep(600)
    except (KeyboardInterrupt, SystemExit):
        print("Exiting...")


def check_uri(uri):
    parsed = urlparse.urlparse(uri)
    if not parsed.scheme in ["http", "https"]:
        raise argparse.ArgumentTypeError(
            "%r is not a valid URL. scheme must be http(s)!" % uri)

    # cut off fragment
    uri = urlparse.urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                               parsed.params, parsed.query, ""))
    return uri


def get_batch_starter_parser():
    parser = argparse.ArgumentParser()

    add_actor_server_params(parser)

    parser.add_argument('--host-name', action="store", default='localhost',
        type=str, help="Interface to bind the started servers to")

    parser.add_argument('-n', '--number', action="store",
        type=int, help='Start n servers',
        required=True
    )

    parser.add_argument('-s', '--start-port', action="store",
        type=int, help="First server's port")
    parser.add_argument('-e', '--exclude-ports', nargs='+',
        type=int, help='Exclude ports')

    parser.add_argument('--save-to-json', action="store",
        type=unicode, help=(
            'Save ports of started servers to a json file.'
            )
    )
    parser.add_argument('--force', action="store_true",
        help='Overwrite a file at save-to-json without asking'
    )

    parser.add_argument('--callback-uri',
        type=check_uri,
        help=(
            "After the servers are started issue a POST request "
            "including used ports to this URI"
        )
    )

    parser.set_defaults(execute_function=start_actor_servers)
    return parser


def main():
    parser = get_batch_starter_parser()
    parsed_args_dct = parser.parse_args().__dict__
    parsed_args_dct.pop('execute_function')(**parsed_args_dct)

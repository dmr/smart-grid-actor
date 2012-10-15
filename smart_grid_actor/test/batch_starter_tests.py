#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from smart_grid_actor.batch_starter import (
    get_batch_starter_parser,
    start_actor_servers
)


def do_parser_test(
        test_instance,
        string,
        server_count=None,
        server_ports=None
        ):
    parsed_args = get_batch_starter_parser().parse_args(string.split())
    #print parsed_args

    parsed_args_dct = parsed_args.__dict__
    kw = parsed_args_dct.pop('execute_function')(
        stop_servers_after_json_save=True,
        **parsed_args_dct
    )

    for _p, process in kw:
        if process.is_alive():
            import time
            time.sleep(.1)
            assert not process.is_alive()

    import pprint
    pprint.pprint(kw)

    started_servers_ports = [port for port, _process in kw]

    if server_count:
        test_instance.assertEqual(len(started_servers_ports), server_count)

    if server_ports:
        test_instance.assertEqual(started_servers_ports, server_ports)

do_parser_test.__test__ = False


class ActorServerCliParserTest(unittest.TestCase):
    def test_number_plus_start_port(self):
        do_parser_test(
            self,
            '--value-range 1 -n4 --start-port 1234',
            server_count=4,
            server_ports=[1234,1235,1236,1237]
        )

    def test_number_is_only_required_param(self):
        do_parser_test(
            self,
            '--value-range 1 -n4',
            server_count=4
        )

    def test_number_plus_start_port_plus_exclude_ports(self):
        do_parser_test(
            self,
            '--value-range 1 -n4 --start-port 1334 --exclude-ports 1335 1336',
            server_count=4,
            server_ports=[1334,1337,1338,1339]
        )

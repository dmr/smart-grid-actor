#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from smart_grid_actor.actor import Actor
from smart_grid_actor.cli_parser import get_parser


default_host_name = 'localhost'
default_port = 9001


def do_parser_test(
        test_instance,
        string,
        expected_actor=None,
        expect_exception=None,
        expected_host_name=default_host_name,
        expected_port=default_port
        ):
    parsed_args = get_parser().parse_args(string.split())
    print parsed_args
    test_instance.assertEqual(
        parsed_args.host_name, expected_host_name,
        msg=parsed_args)
    test_instance.assertEqual(
        parsed_args.port, expected_port,
        msg=parsed_args)

    parsed_args_dct = parsed_args.__dict__

    if expect_exception:
        test_instance.failUnlessRaises(
            expect_exception,
            parsed_args_dct.pop('execute_function'),
            **parsed_args_dct
        )

    if expected_actor:
        kw = parsed_args_dct.pop('execute_function')(**parsed_args_dct)
        assert kw['actor'] == expected_actor, kw

do_parser_test.__test__ = False


class ActorServerCliParserTest(unittest.TestCase):
    def test_default_port_and_hostname(self):
        do_parser_test(
            self,
            '--value-range 1 --dry-run',
            expected_actor=Actor(value=1, value_range=[1])
        )

    def test_actor_hostname_and_port_value(self):
        do_parser_test(
            self,
            '--host-name 127.0.0.1 -p9000 --value-range 1 --dry-run',
            expected_actor=Actor(value=1,
                value_range=[1]),
            expected_host_name='127.0.0.1',
            expected_port=9000
        )

    def test_value_negative_values(self):
        do_parser_test(
            self,
            "--value-range 1 2 3 4 -5 -v-5 --dry-run",
            expected_actor=Actor(value=-5,
                value_range=[1, 2, 3, 4, -5])
        )

    def test_value_failing_values(self):
        # try to set a value outside value range
        do_parser_test(
            self,
            "--value-range 1 -v2 --dry-run",
            expect_exception=ValueError
        )

        do_parser_test(
            self,
            "--value-range 1 -v0 --dry-run",
            expect_exception=ValueError
        )

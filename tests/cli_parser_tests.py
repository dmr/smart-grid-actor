#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from smart_grid_actor.actor import Actor
from smart_grid_actor.cli_parser import get_parser

from _utils import sugarjar_path


default_host_port_tuple = ('localhost', 9001)


def do_parser_test(
        string,
        expected_actor,
        expected_host_port_tuple=default_host_port_tuple
        ):
    parsed_args = get_parser().parse_args(string.split())
    assert parsed_args['host_port_tuple'] == expected_host_port_tuple, \
        parsed_args['host_port_tuple']
    assert parsed_args['actor'] == expected_actor, parsed_args['actor']
do_parser_test.__test__ = False


class ActorServerCliParserTest(unittest.TestCase):
    def test_default_port_and_hostname(self):
        do_parser_test(
            'a --value-range 1 --dry-run',
            Actor(value=1, value_range=[1])
        )

    def test_actor_hostname_and_port_value(self):
        do_parser_test(
            '--host-name 127.0.0.1 -p9000 a --value-range 1 --dry-run',
            Actor(value=1, value_range=[1]),
            expected_host_port_tuple=('127.0.0.1', 9000)
        )

    def test_value_is_set_impicitly(self):
        # note that value=1 was set implicitly in Actor.__init__
        expected_actor = Actor(value=1, value_range=[1,2])

        do_parser_test(
            'a --value-range 1 2 --dry-run',
            expected_actor
        )

    def test_value_negative_values(self):
        do_parser_test(
            "a --value-range 1 2 3 4 -5 -v-5 --dry-run",
            Actor(value=-5, value_range=[1, 2, 3, 4, -5])
        )

    def test_value_failing_values(self):
        self.failUnlessRaises(
            ValueError,
            get_parser().parse_args,
            "a --value-range 1 -v2 --dry-run".split()
        )
        self.failUnlessRaises(
            ValueError,
            get_parser().parse_args,
            "a --value-range 1 -v0 --dry-run".split()
        )


class ControllerActorServerCliParserTest(unittest.TestCase):
    def test_actor_hostname_port_value(self):
        # just one simple test...

        parser = get_parser()
        parsed_args = parser.parse_args(
            'c -a http://localhost:9000 --sugar-jar {0} --dry-run'.format(
                sugarjar_path
            ).split(),
        )

        actor_config = parsed_args['actor'].get_configuration()

        assert actor_config['cls'] == "ControllerActor", \
            actor_config['cls']

        assert actor_config['actors'][0]['cls'] == "RemoteActor",\
            actor_config['actors'][0]['cls']

        assert actor_config['cls'] == "ControllerActor",\
            actor_config['cls']

        assert actor_config['actors'][0]['uri'] == "http://localhost:9000",\
            actor_config['actors'][0]['uri']

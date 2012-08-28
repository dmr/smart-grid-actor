#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attest import Tests, raises, TestBase, test, FancyReporter

from smart_grid_simulation.simulation import Actor
from smart_grid_simulation.cli_parser import parse_actor_server_arguments


default_host_port_tuple = ('localhost', 9001)


def do_parser_test(string, expected_actor,
           expected_host_port_tuple=default_host_port_tuple):
    parsed_args = parse_actor_server_arguments(string.split())
    assert parsed_args['host_port_tuple'] == expected_host_port_tuple, \
        parsed_args['host_port_tuple']
    assert parsed_args['actor'] == expected_actor, parsed_args['actor']


class ActorServerCliParserTest(TestBase):
    @test
    def test_default_port_and_hostname(self):
        do_parser_test('a --value-range 1',
            Actor(value=1, value_range=[1])
        )

    @test
    def test_actor_hostname_and_port_value(self):
        do_parser_test(
            '--host-name 127.0.0.1 -p9000 a --value-range 1',
            Actor(value=1, value_range=[1]),
            expected_host_port_tuple=('127.0.0.1', 9000)
        )

    @test
    def test_value_is_set_impicitly(self):
        # note that value=1 was set implicitly in Actor.__init__
        expected_actor = Actor(value=1, value_range=[1,2])

        do_parser_test('a --value-range 1 2', expected_actor)

    @test
    def test_value_negative_values(self):
        do_parser_test(
            "a --value-range 1 2 3 4 -5 -v-5",
            Actor(value=-5, value_range=[1, 2, 3, 4, -5])
        )

    @test
    def test_value_failing_values(self):
        with raises(ValueError):
            parse_actor_server_arguments(
                "a --value-range 1 -v2".split())
        with raises(ValueError):
            parse_actor_server_arguments(
                "a --value-range 1 -v0".split())


class ControllerActorServerCliParserTest(TestBase):
    @test
    def test_actor_hostname_port_value(self):
        # just one simple test...

        parsed_args = parse_actor_server_arguments(
            'c -a http://localhost:9000'.split(),
            check_remote_actors=False
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


cli_parser_test_suite = Tests([
    ActorServerCliParserTest(),
    ControllerActorServerCliParserTest()
])

if __name__ == '__main__':
    cli_parser_test_suite.run()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attest import Tests, raises, TestBase, test, FancyReporter

sgsim_test = Tests()


@sgsim_test.test
def test_is_installed():
    import smart_grid_simulation
    assert True


from smart_grid_simulation.simulation import (
    AbstractActor, Actor, NotSolvable)


@sgsim_test.test
def test_actor_equality():
    # two actors with same value range and value are equal

    assert Actor(value_range=[2],
        value=2) == Actor(value=2, value_range=[2])
    assert Actor(value=2,
        value_range=[2]) != Actor(value=2,
        value_range=[1,2])
    assert Actor(value=1,
        value_range=[1]) != Actor(value=2,
        value_range=[1,2])
    assert Actor(value=1,
        value_range=[1]) != Actor(value=2,
        value_range=[2])


@sgsim_test.test
def test_AbstractActorInterface():
    actor = AbstractActor()
    assert actor.id is not None
    with raises(NotImplementedError) as error:
        actor.get_value()
    with raises(NotImplementedError) as error:
        actor.get_value_range()
    with raises(NotImplementedError) as error:
        actor.set_value(1)


@sgsim_test.test
def test_if_interface_tests_are_complete():

    from actor_tests import ActorInterface
    from controller_actor_tests import ControllerActorInterface
    from remove_actor_tests import RemoteActorInterface

    methods_for_complete_interface_test = [
        "test_get_value",
        "test_get_value_range",
        "test_set_value_int",
        "test_set_value_int_out_of_range",
        "test_set_value_float",
        "test_set_value_string",
        "test_set_value_string_invalid"
    ]

    for test_cls in ActorInterface, \
                    ControllerActorInterface, RemoteActorInterface:
        for method_name in methods_for_complete_interface_test:
            assert hasattr(test_cls, method_name), \
                "{0} not in {1}".format(method_name, test_cls)


if __name__ == '__main__':
    sgsim_test.run()

    from cli_parser_tests import cli_parser_test_suite
    cli_parser_test_suite.run()

    from actor_tests import actor_classes_suite
    actor_classes_suite.run()

    from controller_actor_tests import controller_actor_classes_suite
    controller_actor_classes_suite.run()

    from remove_actor_tests import remote_actor_classes_suite
    remote_actor_classes_suite.run()
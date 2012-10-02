#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest


def test_smart_grid_simulation_is_installed():
    import smart_grid_simulation
    assert True


from smart_grid_simulation.simulation import (
    AbstractActor, Actor, NotSolvable)


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


class TestAbstractActorInterface(unittest.TestCase):
    def test(self):
        actor = AbstractActor()
        assert actor.id is not None
        self.failUnlessRaises(
            NotImplementedError,
            actor.get_value
        )
        self.failUnlessRaises(
            NotImplementedError,
            actor.get_value_range
        )
        self.failUnlessRaises(
            NotImplementedError,
            actor.set_value,
            1
        )


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

    for test_cls in (ActorInterface,
                     ControllerActorInterface,
                     RemoteActorInterface):
        for method_name in methods_for_complete_interface_test:
            assert hasattr(test_cls, method_name),\
            "{0} not in {1}".format(method_name, test_cls)

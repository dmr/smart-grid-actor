#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from smart_grid_actor.actor import AbstractActor, Actor
from smart_grid_actor.test.actor_tests import ActorInterface


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
    methods_for_complete_interface_test = [
        "test_get_value",
        "test_get_value_range",
        "test_set_value_int",
        "test_set_value_int_out_of_range",
        "test_set_value_float",
        "test_set_value_string",
        "test_set_value_string_invalid"
    ]

    for test_cls in [ActorInterface]:
        for method_name in methods_for_complete_interface_test:
            assert hasattr(test_cls, method_name),\
            "{0} not in {1}".format(method_name, test_cls)

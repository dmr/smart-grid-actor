#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest2

from smart_grid_actor.actor import AbstractActor, Actor
from smart_grid_actor.test.actor_tests import ActorInterface


def test_actor_equality():
    # two actors with same value range and value are equal
    a_1 = Actor(value=2, value_range=[2])
    a_2 = Actor(value=2, value_range=[2])
    a_3 = Actor(value=2, value_range=[1, 2])
    a_4 = Actor(value=1, value_range=[1, 2])
    a_5 = Actor(value_range=[1, 2]) # initialized with min(value_range)

    assert a_1 == a_2
    assert a_1 != a_3
    assert a_3 != a_4
    assert a_4 == a_5


class TestAbstractActor(unittest2.TestCase):
    def test_abstract_interface(self):
        actor = AbstractActor()
        assert actor.id is not None

        with self.assertRaises(NotImplementedError):
            actor.get_value()

        with self.assertRaises(NotImplementedError):
            actor.get_value_range()

        with self.assertRaises(NotImplementedError):
            actor.set_value(1)


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
            assert hasattr(test_cls, method_name), \
                "{0} not in {1}".format(method_name, test_cls)

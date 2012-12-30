#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest2 as unittest

from smart_grid_actor.actor import (
    AbstractActor, Actor, NotSolvable, ConfigurationException
)

from smart_grid_actor.test._utils import AbstractInterface


class ActorIdGeneration(unittest.TestCase):
    def test_generates_increasing_numbers(self):
        a1 = AbstractActor()
        a2 = AbstractActor()

        self.assert_(a2.id > a1.id)

        a3 = AbstractActor()
        self.assert_(a3.id > a2.id)

    def test_converts_to_int(self):
        a1 = AbstractActor("1000", id_collection=set([]))
        self.assertEqual(a1.id, 1000)

    def test_prevents_duplicate_ids(self):
        a1 = AbstractActor()
        with self.assertRaises(ConfigurationException):
            AbstractActor(a1.id)

    def test_prevents_invalid_input(self):
        with self.assertRaises(ValueError):
            AbstractActor("a")

    def test_used_by_subclasses(self):
        a1 = Actor(value_range=[1], id=123, id_collection=set([]))
        self.assertEqual(a1.id, 123)


def get_actor(
        value_range=range(1, 3+1),
        value=1
        ):
    return value_range, Actor(value=value,
        value_range=value_range
    )


class ActorInterface(AbstractInterface, unittest.TestCase):
    def setUp(self):
        self.value_range, self.a1 = get_actor()


class ActorInit(unittest.TestCase):
    def test_valid_init_vr_no_value_returns_min_vr(self):
        # value is set implicitly
        actor = Actor([1, 2])
        assert actor.id
        self.assertEqual(actor.get_value(), 1) #min([1, 2])

    def test_valid_init_vr_and_value(self):
        v = 2
        actor = Actor([1, 2], value=v)
        assert actor.id
        self.assertEqual(actor.get_value(), v)

    def test_invalid_init(self):
        with self.assertRaises(ValueError):
            Actor(["1", 2])
        with self.assertRaises(ValueError):
            Actor([1], value=0)
        with self.assertRaises(ValueError):
            Actor([1], value=2)

    def test_invalid_init_vr_and_value_out_of_vr(self):
        with self.assertRaises(ValueError):
            Actor([1, 2], value=3)
        with self.assertRaises(ValueError):
            Actor([1, 2], value="drei")


class ActorInterfaceNegativeRange(unittest.TestCase):
    def setUp(self):
        self.value_range, self.a1 = get_actor(
            range(-10, -2+1),
            value=-5
        )

    def test_set_value(self):
        self.assertEqual(self.a1.get_value(), -5)
        self.a1.set_value(-10)
        self.assertEqual(self.a1.get_value(), -10)
        value_range = self.a1.get_value_range()
        self.assertEqual(value_range, set(self.value_range))

    def test_set_value_out_of_boundary1(self):
        with self.assertRaises(NotSolvable):
            self.a1.set_value(-20)

    def test_control(self):
        with self.assertRaises(NotSolvable):
            self.a1.set_value(0)


class ActorInterfaceValueRange(unittest.TestCase):
    def test_nonempty_value(self):
        actor = Actor([1, 1, 1, 2])
        assert actor.id
        self.assertEqual(actor.get_value_range(), set([1, 2]))

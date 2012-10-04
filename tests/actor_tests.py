#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from smart_grid_actor.actor import (
    AbstractActor, Actor, NotSolvable, ConfigurationException,
)

from _utils import AbstractInterface


def get_actor(
        value_range=range(1,3+1),
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
        vr = [1,2]
        actor = Actor(vr)
        assert actor.id
        assert actor.get_value() == 1

    def test_valid_init_vr_and_value(self):
        vr = [1,2]
        v = 2
        actor = Actor(vr, value=v)
        assert actor.id
        assert actor.get_value() == 2

    def test_invalid_init(self):
        vr = ["1",2]
        self.failUnlessRaises(
            ValueError,
            Actor,
            vr
        )

        self.failUnlessRaises(
            ValueError,
            Actor,
            value_range=[1], value=0
        )

        self.failUnlessRaises(
            ValueError,
            Actor,
            value_range=[1], value=2
        )

    def test_invalid_init_vr_and_value_out_of_vr(self):
        vr = [1,2]
        v = 3
        self.failUnlessRaises(
            ValueError,
            Actor,
            vr, value=v
        )

    def test_invalid_init_vr_and_value_out_of_vr(self):
        vr = [1,2]
        v = "drei"
        self.failUnlessRaises(
            ValueError,
            Actor,
            vr, value=v
        )


class ActorInterfaceNegativeRange(unittest.TestCase):
    def setUp(self):
        self.value_range, self.a1 = get_actor(
            range(-10, -2+1),
            value=-5
        )

    def test_set_value(self):
        assert self.a1.get_value() == -5
        self.a1.set_value(-10)
        assert self.a1.get_value() == -10
        value_range = self.a1.get_value_range()
        assert value_range == set(self.value_range)

    def test_set_value_out_of_boundary1(self):
        self.failUnlessRaises(
            NotSolvable,
            self.a1.set_value,
            -20
        )

    def test_control(self):
        self.failUnlessRaises(
            NotSolvable,
            self.a1.set_value,
            0
        )


class ActorInterfaceValueRange(unittest.TestCase):
    def test_nonempty_value(self):
        vr = [1,1,1,2]
        actor = Actor(vr)
        assert actor.id
        assert actor.get_value_range() == set([1,2])

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attest import Tests, raises, TestBase, test, FancyReporter

from smart_grid_simulation.simulation import Actor, NotSolvable


class ActorInterface(TestBase):
    def __context__(self):
        self.value_range = range(1,6+1)
        assert max(self.value_range) == 6
        self.a1 = Actor(value=5,
            value_range=self.value_range)
        yield
        del self.a1

    @test
    def test_get_value(self):
        a1_value =  self.a1.get_value()
        assert a1_value == 5
        assert type(a1_value) == int

    @test
    def test_get_value_range(self):
        a1_vr = self.a1.get_value_range()
        assert a1_vr == set(self.value_range)
        assert type(a1_vr) == set

    @test
    def test_set_value_int(self):
        ret_val = self.a1.set_value(2)

        assert ret_val == 2

        a1_value =  self.a1.get_value()
        assert a1_value == 2
        assert type(a1_value) == int

    @test
    def test_set_value_int_out_of_range(self):
        with raises(NotSolvable) as error:
            self.a1.set_value(0)

    @test
    def test_set_value_float(self):
        assert self.a1.get_value() == 5
        self.a1.set_value(1.1)

        a1_value =  self.a1.get_value()
        assert a1_value == 1
        assert type(a1_value) == int

    @test
    def test_set_value_string(self):
        assert self.a1.get_value() == 5
        self.a1.set_value("1")

        a1_value =  self.a1.get_value()
        assert a1_value == 1
        assert type(a1_value) == int

    @test
    def test_set_value_string_invalid(self):
        assert self.a1.get_value() == 5
        with raises(NotSolvable) as error:
            self.a1.set_value("Zwei")
        assert self.a1.get_value() == 5


class ActorInit(TestBase):
    @test
    def test_valid_init_vr_no_value_returns_min_vr(self):
        vr = [1,2]
        actor = Actor(vr)
        assert actor.id
        assert actor.get_value() == 1

    @test
    def test_valid_init_vr_and_value(self):
        vr = [1,2]
        v = 2
        actor = Actor(vr, value=v)
        assert actor.id
        assert actor.get_value() == 2

    @test
    def test_invalid_init(self):
        vr = ["1",2]
        with raises(ValueError):
            actor = Actor(vr)

        with raises(ValueError):
            Actor(value_range=[1], value=0)
        with raises(ValueError):
            Actor(value_range=[1], value=2)

    @test
    def test_invalid_init_vr_and_value_out_of_vr(self):
        vr = [1,2]
        v = 3
        with raises(ValueError) as exc:
            actor = Actor(vr, value=v)

    @test
    def test_invalid_init_vr_and_value_out_of_vr(self):
        vr = [1,2]
        v = "drei"
        with raises(ValueError) as exc:
            actor = Actor(vr, value=v)


class ActorInterfaceNegativeRange(TestBase):
    def __context__(self):
        self.value_range = range(-10, -2+1)
        self.a1 = Actor(value=-5,
            value_range=self.value_range)
        yield
        del self.a1

    @test
    def test_set_value(self):
        assert self.a1.get_value() == -5
        self.a1.set_value(-10)
        assert self.a1.get_value() == -10
        value_range = self.a1.get_value_range()
        assert value_range == set(self.value_range)

    @test
    def test_set_value_out_of_boundary1(self):
        with raises(NotSolvable) as error:
            self.a1.set_value(-20)

    @test
    def test_control(self):
        with raises(NotSolvable) as error:
            self.a1.set_value(0)


class ActorInterfaceValueRange(TestBase):
    @test
    def test_nonempty_value(self):
        vr = [1,1,1,2]
        actor = Actor(vr)
        assert actor.id
        assert actor.get_value_range() == set([1,2])


actor_classes_suite = Tests([
    ActorInit(),
    ActorInterface(),
    ActorInterfaceNegativeRange(),
    ActorInterfaceValueRange(),
])

if __name__ == '__main__':
    actor_classes_suite.run()
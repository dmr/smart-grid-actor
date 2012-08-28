#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attest import Tests, raises, TestBase, test, FancyReporter

from smart_grid_simulation.simulation import (Actor,
                                              ControllerActor,
                                              NotSolvable)

from _utils import csp_solver_config

class ControllerActorInterface(TestBase):
    def __context__(self):
        self.a1 = Actor([1, 3])
        self.a2 = Actor(range(-10, -7+1))
        yield
        del self.a1
        del self.a2

    @test
    def test_init_raises_exception_not_an_actor(self):
        with raises(Exception) as error:
            ControllerActor(actors=[self.a1, self.a2, '3'])

    @test
    def test_init(self):
        a3 = ControllerActor(actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config)
        assert a3.id

    @test
    def test_get_value(self):
        a3 = ControllerActor(actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config)

        assert self.a1.get_value() == 1, self.a1.get_value()
        assert self.a2.get_value() == -10, self.a2.get_value()

        a3_value = a3.get_value()
        assert type(a3_value) == int
        assert a3_value == -9

    @test
    def test_get_value_range(self):
        a3 = ControllerActor(actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config)
        a3_value_range = a3.get_value_range()
        assert a3_value_range == set([-9, -8, -7, -6, -5, -4]), \
            a3_value_range

    @test
    def test_set_value_int(self):
        a3 = ControllerActor(actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config)
        assert self.a1.get_value() == 1, self.a1.get_value()
        assert self.a2.get_value() == -10, self.a2.get_value()
        assert a3.get_value() == -9, a3.get_value()

        ret_val = a3.set_value(-4)

        assert ret_val == -4

        assert self.a1.get_value() == 3, self.a1.get_value()
        assert self.a2.get_value() == -7, self.a2.get_value()
        assert a3.get_value() == -4, a3.get_value()

    @test
    def test_set_value_int_out_of_range(self):
        a3 = ControllerActor(actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config)
        with raises(NotSolvable) as error:
            a3.set_value(0)

    @test
    def test_set_value_float(self):
        a3 = ControllerActor(actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config)
        assert self.a1.get_value() == 1, self.a1.get_value()
        assert self.a2.get_value() == -10, self.a2.get_value()
        assert a3.get_value() == -9, a3.get_value()

        ret_val = a3.set_value(-4.5)

        assert ret_val == -4

        assert self.a1.get_value() == 3, self.a1.get_value()
        assert self.a2.get_value() == -7, self.a2.get_value()
        assert a3.get_value() == -4, a3.get_value()

    @test
    def test_set_value_string(self):
        a3 = ControllerActor(actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config)
        assert self.a1.get_value() == 1, self.a1.get_value()
        assert self.a2.get_value() == -10, self.a2.get_value()
        assert a3.get_value() == -9, a3.get_value()

        a3.set_value("-4")

        assert self.a1.get_value() == 3, self.a1.get_value()
        assert self.a2.get_value() == -7, self.a2.get_value()
        assert a3.get_value() == -4, a3.get_value()
        assert type(a3.get_value()) == int

    @test
    def test_set_value_string_invalid(self):
        a3 = ControllerActor(actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config)
        with raises(NotSolvable) as error:
            a3.set_value("null")


class ControllerOfControllserActorInterface(TestBase):
    def __context__(self):
        self.a1 = Actor([5, 6])
        self.a2 = Actor([7, 8])
        self.a3 = ControllerActor(actors=[self.a1, self.a2],
            csp_solver_config=csp_solver_config)

        self.a4 = Actor([-5, -6])
        self.a5 = Actor([-7, -8])
        self.a6 = ControllerActor(actors=[self.a4, self.a5],
            csp_solver_config=csp_solver_config)

        yield
        for a in [self.a1, self.a2, self.a3,
                  self.a4, self.a5, self.a6,]:
            del a

    @test
    def test_set_value_failure_str(self):
        a7 = ControllerActor(actors=[self.a3, self.a6],
            csp_solver_config=csp_solver_config)

        a7_vr = a7.get_value_range()
        assert a7_vr == [-2, -1, 0, 1, 2], a7_vr

    @test
    def test_set_value_failure_str(self):
        a7 = ControllerActor(actors=[self.a3, self.a6],
            csp_solver_config=csp_solver_config)

        a7.set_value(0)

        a7_value = a7.get_value()
        assert a7_value == 0, a7_value


controller_actor_classes_suite = Tests([
    ControllerActorInterface(),
    ControllerOfControllserActorInterface()
])


if __name__ == '__main__':
    controller_actor_classes_suite.run()
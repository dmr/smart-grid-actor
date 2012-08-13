#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attest import Tests, raises

sgsim_test = Tests()


@sgsim_test.test
def test_is_installed():
    import smart_grid_simulation
    assert True


import smart_grid_simulation
from smart_grid_simulation.simulation import (AbstractActor, Actor,
                                              ControllerActor, RemoteActor,
                                              NotSolvable)
from smart_grid_simulation.cli_parser import parse_actor_server_arguments


@sgsim_test.test
def test_actor_equality():
    assert Actor(2, [2]) == Actor(2, [2])
    assert Actor(2, [2]) != Actor(2, [1,2])
    assert Actor(1, [1]) != Actor(2, [1,2])
    assert Actor(1, [1]) != Actor(2, [2])


@sgsim_test.test
def test_parser():
    assert parse_actor_server_arguments(
        ['--host-name', '127.0.0.1', '-p', '9000', 'a', '-v', '2']
    ) == dict(host_port_tuple=('127.0.0.1', 9000), actor=Actor(2, [2]))


@sgsim_test.test
class TestAbstractActorInterface():
    def test_interface(self):
        actor = AbstractActor(1,[1])
        assert actor.id
        with raises(NotImplementedError) as error:
            actor.get_value()
        with raises(NotImplementedError) as error:
            actor.get_value_range()
        with raises(NotImplementedError) as error:
            actor.set_value(1)

@sgsim_test.test
class TestAbstractActorInterface():
    def test_interface(self):
        v = 1
        vr = [1,2]
        actor = Actor(v,vr)
        assert actor.id
        assert actor.get_value() == v
        assert actor.get_value_range()

    def test_set_value(self):
        v = 1
        vr = [1,2]
        actor = Actor(v,vr)

        assert actor.get_value() == v

        actor.set_value(2)
        assert actor.get_value() == 2

        with raises(NotSolvable) as error:
            actor.set_value(3)

class BasicControlOperationsTestMixin(object):
    def setUp(self): # TODO implement
        raise NotImplementedError('please subclass')

class SingleActor1(BasicControlOperationsTestMixin):
    def setUp(self):
        value_range=range(1,6+1)
        assert max(value_range=6)
        self.a1 = Actor(value=5, value_range=value_range)

    def test_set_value(self):
        assert self.a1.get_value() == 5
        self.a1.set_value(1)
        assert self.a1.get_value() == 1
        assert self.a1.get_value_range() == range(1, 6+1)

    def test_control(self):
        with raises(NotImplementedError) as error:
            self.a1.set_value(0)

    def test_controlled(self):
        assert self.a1.get_value() == 5
        self.a1.set_value(2)
        assert self.a1.get_value() == 2


class SingleActor2(BasicControlOperationsTestMixin):
    def setUp(self):
        value_range = range(-10, -2+1)
        self.a1 = Actor(value=-5, value_range=value_range)

    def test_set_value(self):
        assert self.a1.get_value() == -5
        self.a1.set_value(-10)
        assert self.a1.get_value() == -10
        self.a1._old_value == [-5]
        assert 0, 'impl!'
        self.a1.set_value(-10)
        self.a1._old_value == [-5, -10]
        assert self.a1.value_range() == range(-10, -2+1)

    def test_set_value_out_of_boundary1(self):
        with raises(NotImplementedError) as error:
            assert self.a1.get_value() == -20
        #TODO: implement "soft fail" --> limit to boudaries?
        #self.a1.set_value(-20)
        #assert self.a1.get_value() == -10

    def test_control(self):
        with raises(NotImplementedError) as error:
            self.a1.set_value(0)


class ActorControllingActors1():
    def setUp(self):
        self.a1 = simulation.LocalActor(value=5, value_min=1, value_max=15)
        self.a2 = simulation.LocalActor(value=-5, value_min=-10, value_max=-2)
        self.a3 = simulation.LocalControllerOfActors(actors=[self.a1, self.a2,])

    def test_value_range(self):
        self.assertEqual(self.a3.value_range(), range(-9, 14)) # manuell ermittelt!

    def test_do_control_successful(self):
        self.a3.set_value(0)
        self.assertEqual(self.a1.get_value(), -self.a2.get_value())
        self.assertEqual(self.a3.get_value(), 0)

    def test_do_control_fails(self):
        self.assertRaises(simulation.NotSolvable, self.a3.set_value, 15)


class ActorControllingActors2():
    def setUp(self):
        self.a1 = simulation.LocalActor(value=6, value_min=6, value_max=7)
        self.a2 = simulation.LocalActor(value=-5, value_min=-5, value_max=-4)
        self.a3 = simulation.LocalControllerOfActors(actors=[self.a1,self.a2,])

    def test_value_range(self):
        self.assertEqual(self.a3.value_range(), [1,2,3]) # manuell ermittelt!


class ActorControllingActorsControllingActors1():
    def setUp(self):
        self.a1 = simulation.LocalActor(value=5, value_min=1, value_max=15)
        self.a2 = simulation.LocalActor(value=-5, value_min=-10, value_max=-2)
        self.a3 = simulation.LocalControllerOfActors(actors=[self.a1,self.a2,])
        self.a4 = simulation.LocalActor(value=-9, value_min=-10, value_max=-8)
        self.a5 = simulation.LocalControllerOfActors(actors=[self.a3, self.a4,])

    def test_do_control_successful(self):
        self.a5.set_value(0)

        self.assertEqual(self.a5.get_value(), 0)

        self.assertEqual(self.a3.get_value(), -self.a4.get_value())

        self.assertEqual(self.a1.get_value()+self.a2.get_value()\
                         +self.a4.get_value(), 0)

        print self.a5 #test __repr__

#def test_do_control_expexted_output():
#    a1 = simulation.LocalActor(value=5, value_min=1, value_max=15)
#    a2 = simulation.LocalActor(value=-5, value_min=-10, value_max=-2)
#    a3 = simulation.LocalControllerOfActors(actors=[a1, a2,])
#    a4 = simulation.LocalActor(value=-9, value_min=-10, value_max=-8)
#    a5 = simulation.LocalControllerOfActors(actors=[a3, a4,])

class ActorValueRange():
    def test_simple(self):
        a = simulation.LocalActor(value=5, value_min=1, value_max=5)
        self.assertEqual(a.value_range(), [1,2,3,4,5])

    def test_combined_actor1(self):
        for config in [
            ([(-12, -10), (7, 9),],
             [-5, -4, -3, -2, -1]),
            ([(-122, -10), (0, 1),],
             range(-122, -9+1)),
            ([(-12,-10), (0,1), (2,6), (10,77)],
             range(0, 74+1)),
            ([(-12, -11), (0, 1),],
             [-12, -11, -10]),
        ]:
            actors = []
            for minimum, maximum in config[0]:
                actors.append(simulation.LocalActor(value_min=minimum, value_max=maximum))
            self.assertEqual(simulation.LocalControllerOfActors(
                actors=actors).value_range(), config[1])


class TestInterface():
    def test_actor(self):
        a = simulation.LocalActor(1,1)
        self.assertEqual(a.get_serialized_value(), json.dumps(
                {'value':1, 'value_range':[1], 'duration':'PT1H'}))


class SimulationTestBasicFunction():
    def test_2LocalActors_in_LocalController(self):
        # 1. test basic function local actors
        a1 = simulation.LocalActor(value_min=1, value_max=5)
        self.assertEqual(a1.get_value(), 5)
        a1.set_value(2)
        self.assertEqual(a1.get_value(), 2)

        a2 = simulation.LocalActor(value_min=-5, value_max=-4)
        self.assertEqual(a2.get_value(), -4)
        a2.set_value(-5)
        self.assertEqual(a2.get_value(), -5)

        # 2. define controller
        c1 = simulation.LocalControllerOfActors([a1,a2])
        c1.set_value(1)
        self.assertEqual(a1.get_value(), 5)
        self.assertEqual(a2.get_value(), -4)
        self.assertRaises(simulation.NotSolvable, c1.set_value, 2)


class ControllerOfControllers():
    def test_basic_function(self):
        controllers = [
        simulation.LocalControllerOfActors(actors=[
        simulation.LocalActor(value_min=1,value_max=2) for _a in range(2)])
        for _c in range(2)]
        actor = simulation.LocalControllerOfActors(actors=controllers)
        self.assertEqual(actor.value_range(), [4, 5, 6, 7, 8])
        actor.set_value(min(actor.value_range()))
        self.assertEqual(actor.get_value(), 4)

    def test_real_actor_count(self):
        a1 = simulation.LocalActor(value_min=1,value_max=2)
        self.assertEqual(a1.real_actor_count(), 1)
        a2 = simulation.LocalActor(value_min=1,value_max=2)
        a3 = simulation.LocalControllerOfActors(actors=[a1,a2])
        self.assertEqual(a3.real_actor_count(), 2)
        a4 = simulation.LocalActor(1,1)
        a5 = simulation.LocalControllerOfActors(actors=[a3,a4])
        self.assertEqual(a5.real_actor_count(), 3)


#class ConsistentHierarchy(unittest2.TestCase):
#    def test_wrong_definition_raises_error(self):
#        a1 = simulation.LocalActor(value_min=1,value_max=2)
#        a2 = simulation.LocalActor(value_min=1,value_max=2)
#        a3 = simulation.LocalControllerOfActors(actors=[a1,a2])
#        # TODO: implement
#        self.assertRaises(ValueError, simulation.LocalControllerOfActors, [a3,a1])
#    def test_wrong_definition_raises_error_across_hierarchies(self): # more than one layer




if __name__ == '__main__':
    sgsim_test.run()

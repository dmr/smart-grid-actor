#!/usr/bin/env python
# -*- coding: utf-8 -*-
from attest import Tests, raises, TestBase, test, FancyReporter

from smart_grid_simulation.simulation import (RemoteActor,
                                              NotSolvable,
                                              ControllerActor,
                                              Actor)

from smart_grid_simulation.cli_parser import parse_actor_server_arguments
from smart_grid_simulation.server import start_actor_server

from _utils import csp_solver_config


class RemoteActorInterface(TestBase):
    def __context__(self):
        port = 9005
        vr = [1,2,3]
        args = '-p={0} a --value-range {1}'.format(
            port, " ".join([str(v) for v in vr])
        )
        sys_args = args.split()
        parsed_args = parse_actor_server_arguments(sys_args=sys_args)
        _port, actor_server_process = start_actor_server(
            start_in_background_thread=True,
            **parsed_args
        )

        self.a1 = RemoteActor(uri="http://localhost:{0}".format(port))
        yield
        actor_server_process.terminate()
        actor_server_process.join()
        del self.a1

    @test
    def test_get_value(self):
        a1_value =  self.a1.get_value()
        assert a1_value == 1
        assert type(a1_value) == int

    @test
    def test_get_value_range(self):
        a1_value_range =  self.a1.get_value_range()
        assert a1_value_range == set([1,2,3])

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
        assert self.a1.get_value() == 1
        self.a1.set_value(2.1)

        a1_value =  self.a1.get_value()
        assert a1_value == 2
        assert type(a1_value) == int

    @test
    def test_set_value_string(self):
        assert self.a1.get_value() == 1
        self.a1.set_value("2")

        a1_value =  self.a1.get_value()
        assert a1_value == 2
        assert type(a1_value) == int

    @test
    def test_set_value_string_invalid(self):
        assert self.a1.get_value() == 1
        with raises(NotSolvable) as error:
            self.a1.set_value("Zwei")
        assert self.a1.get_value() == 1


class RemoteActorControllingControllerActorOfActorInterface(RemoteActorInterface):
    def __context__(self):
        vr = [1,2,3]

        port, actor_server_process = start_actor_server(
            start_in_background_thread=True,
            actor=ControllerActor(
                actors=[
                    Actor(value_range=vr)
                ],
                csp_solver_config=csp_solver_config
            )
        )

        self.a1 = RemoteActor(uri="http://localhost:{0}".format(port))
        yield
        actor_server_process.terminate()
        actor_server_process.join()
        del self.a1


class RemoteActorControllingControllerActorOfRemoteActorInterface(RemoteActorInterface):
    def __context__(self):
        vr = [1,2,3]

        port_1, actor_server_process_1 = start_actor_server(
            start_in_background_thread=True,
            actor=Actor(value_range=vr)
        )

        port_2, actor_server_process_2 = start_actor_server(
            start_in_background_thread=True,
            actor=ControllerActor(
                actors=[
                    RemoteActor(uri="http://localhost:{0}".format(port_1))
                ],
                csp_solver_config=csp_solver_config
            )
        )

        self.a1 = RemoteActor(uri="http://localhost:{0}".format(port_2))
        yield
        actor_server_process_1.terminate()
        actor_server_process_1.join()
        actor_server_process_2.terminate()
        actor_server_process_2.join()
        del self.a1


remote_actor_classes_suite = Tests([
    RemoteActorInterface(),
    RemoteActorControllingControllerActorOfActorInterface(),
    RemoteActorControllingControllerActorOfRemoteActorInterface()
])

if __name__ == '__main__':
    remote_actor_classes_suite.run()
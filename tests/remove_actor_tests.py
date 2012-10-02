#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import unittest

from smart_grid_simulation.simulation import (RemoteActor,
                                              ControllerActor,
                                              Actor)
from smart_grid_simulation.server import start_actor_server

from _utils import (
    csp_solver_config,
    AbstractInterface
)

class RemoteActorInterface(AbstractInterface, unittest.TestCase):
    def setUp(self):
        port, self._actor_server_process = start_actor_server(
            start_in_background_thread=True,
            actor=Actor(value_range=[1,2,3])
        )
        self.a1 = RemoteActor(uri="http://localhost:{0}".format(port))
        time.sleep(1)

    def tearDown(self):
        self._actor_server_process.terminate()
        self._actor_server_process.join()


class RemoteActorControllingControllerActorOfActorInterface(
    AbstractInterface, unittest.TestCase
):
    def setUp(self):
        port, self._actor_server_process = start_actor_server(
            start_in_background_thread=True,
            actor=ControllerActor(
                actors=[
                    Actor(value_range=[1,2,3])
                ],
                csp_solver_config=csp_solver_config
            )
        )
        self.a1 = RemoteActor(uri="http://localhost:{0}".format(port))
        time.sleep(1)

    def tearDown(self):
        self._actor_server_process.terminate()
        self._actor_server_process.join()


class RemoteActorControllingControllerActorOfRemoteActorInterface(
    AbstractInterface, unittest.TestCase
):
    def setUp(self):
        port_1, self._actor_server_process_1 = start_actor_server(
            start_in_background_thread=True,
            actor=Actor(value_range=[1,2,3])
        )
        port_2, self._actor_server_process_2 = start_actor_server(
            start_in_background_thread=True,
            actor=ControllerActor(
                actors=[
                    RemoteActor(uri="http://localhost:{0}".format(port_1))
                ],
                csp_solver_config=csp_solver_config
            )
        )
        self.a1 = RemoteActor(uri="http://localhost:{0}".format(port_2))
        time.sleep(1)

    def tearDown(self):
        self._actor_server_process_1.terminate()
        self._actor_server_process_1.join()
        self._actor_server_process_2.terminate()
        self._actor_server_process_2.join()

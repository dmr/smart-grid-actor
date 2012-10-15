import json
import unittest

import requests

from smart_grid_actor.server import start_actor_server
from smart_grid_actor.actor import Actor


def assure_response(
        test_class_instance,
        response,
        expected_status_code=200,
        expected_content_type="application/json",
        expected_content=None
        ):
    import pprint
    pprint.pprint(response.__dict__)
    test_class_instance.failUnlessEqual(
        response.status_code,
        expected_status_code
    )
    test_class_instance.failUnlessEqual(
        response.headers['content-type'],
        expected_content_type
    )
    assert expected_content
    if expected_content_type == "application/json":
        response_content = json.loads(response.content)
    else:
        response_content = response.content
    test_class_instance.failUnlessEqual(
        response_content,
        expected_content
    )


class HttpInterfaceTestActor(unittest.TestCase):
    def setUp(self):
        self.vr = [1,2]
        self.a1 = Actor(value_range=[1,2], value=1)
        self.port, server_process = start_actor_server(
            actor=self.a1,
            start_in_background_thread=True,
            log_to_std_err=True
        )
        self.processes = [server_process]

    def tearDown(self):
        for p in self.processes:
            p.terminate()
            p.join() # frees up the socket for next scenario

    def url(self, path):
        return u"http://{host}:{port}{path}".format(
            host='localhost', port=self.port, path=path
        )

    def query(self, path):
        return requests.get(self.url(path), allow_redirects=False)

    def update(self, path, put_data):
        return requests.put(self.url(path), put_data,
            allow_redirects=False
        )

    def test_query_consumption(self):
        assure_response(
            self,
            response=self.query('/'),
            expected_content={'value':1}
        )

    def test_query_value_range(self):
        assure_response(
            self,
            response=self.query('/'),
            expected_content={'value':1}
        )

    def test_value_update(self):
        assure_response(
            self,
            response=self.update('/', "2"),
            expected_content={'value':2}
        )
        assure_response(
            self,
            response=self.query('/'),
            expected_content={'value':2}
        )

    def test_value_update_wrong_input(self):
        assure_response(
            self,
            response=self.update('/', "3"),
            expected_status_code=400,
            expected_content_type="text/html",
            expected_content="Input error: 3 not in value_range [1, 2]"
        )
        assure_response(
            self,
            response=self.query('/'),
            expected_content={'value':1}
        )

    def test_value_update_wrong_input_string(self):
        assure_response(
            self,
            response=self.update('/', "drei"),
            expected_status_code=400,
            expected_content_type="text/html",
            expected_content="Input error: Not a valid integer: 'drei'"
        )
        assure_response(
            self,
            response=self.query('/'),
            expected_content={'value':1}
        )

    def test_actor_returns_redirect(self):
        assure_response(
            self,
            response=self.query('/wrong'),
            expected_status_code=301,
            expected_content_type="text/html",
            expected_content="Moved permanently: /"
        )

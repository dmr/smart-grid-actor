# -*- coding: utf-8 -*-
import json

import requests

from behave import when, then, given

import utils

@given(u'ActorServer with vr {vr} on port {port}')
def actor_server_with_vr_on_port(context, vr, port):
    vr = eval(vr)
    utils.add_actor_server_to_context(context, port, vr)


@when(u'I query {port} "{path}"')
def when_i_query(context, port, path):
    context.response = requests.get(
        u"http://{host}:{port}{path}".format(
            host='localhost', port=port, path=path)
    )

@when(u'I update {port} "{path}" with "{content}"')
def when_i_update(context, port, path, content):
    context.response = requests.put(
        u"http://{host}:{port}{path}".format(
            host='localhost', port=port, path=path),
        data=content)


@then(u'I receive status {status_code}')
def then_i_receive_status(context, status_code):
    #import ipdb; ipdb.set_trace()
    the_status_code = int(status_code)
    assert context.response.status_code == the_status_code, \
        str(context.response.status_code) + ' ' + context.response.text


@then(u'I receive json "{expected_resp_content}"')
def then_i_receive_json(context, expected_resp_content):
    assert context.response.headers['content-type'] == 'application/json',\
        context.response.headers['content-type']
    expected_resp = json.dumps(eval(expected_resp_content))
    assert context.response.text == expected_resp, context.response.text


@then(u'actor {port} value is "{expected_resp_content}"')
def current_actor_value(context, port, expected_resp_content):
    response = requests.get(
        u"http://{host}:{port}{path}".format(
            host='localhost', port=port, path='/')
    )
    expected_resp = json.dumps(eval(expected_resp_content))
    assert response.text == expected_resp, response.text


@then(u'I receive content "{expected_resp}"')
def then_i_receive_content(context, expected_resp):
    assert context.response.text == expected_resp, context.response.text

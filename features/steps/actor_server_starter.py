from behave import when, then, given

import utils

@given(u'the Actors')
def given_the_actors(context):
    for row in context.table:
        port = int(row['port'])
        vr = eval(row['value_range'])
        utils.add_actor_server_to_context(context, port, vr=vr)

@given(u'the Controllers')
def given_the_controllers(context):
    for row in context.table:
        port = int(row['port'])
        actors = eval(row['actors'])
        utils.add_actor_server_to_context(context, port, actors=actors)

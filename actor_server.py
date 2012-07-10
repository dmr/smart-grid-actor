#!/usr/bin/env python
# -*- coding: utf-8 -*-

import StringIO

import eventlet
import eventlet.wsgi
from eventlet.green import urllib2

eventlet.monkey_patch(all=True)


def fetch_uri(uri):
    try:
        return urllib2.urlopen(uri).read()
    except urllib2.URLError as exc:
        print "Error processing", uri, exc.reason
        return "0"


def get_value(environ, start_response, response_headers, actor):
    # convert output value to string
    output = str(actor.get_value())
    response_headers.append(('Content-Type', 'text/json'))
    response_headers.append(('Content-Length', str(len(output))))
    start_response('200 OK', response_headers)
    return [output]


def set_value(environ, start_response, response_headers, actor):
    data = environ['wsgi.input'].read()
    try:
        actor.set_value(data)
    except Exception:
        print 'please pass integer value (converted to unicode by urllib...)'
        start_response('400 Bad Request', response_headers)
        return ['Integer input required']
    output = actor.get_value()
    response_headers.append(('Content-type', 'text/json'))
    response_headers.append(('Content-Length', str(len(output))))
    start_response('200 OK', response_headers)


def return_405(environ, start_response):
    start_response('405 Method not allowed', [])
    return ['GET (Accept text/json) and PUT (integer) allowed']


def get_application(actor, host_uri):
    def application(environ, start_response):
        #print environ
        response_headers = [('Host', host_uri),
            ('Content-Location', environ['PATH_INFO'])]

        if environ['PATH_INFO'] != '/':
            start_response('301 Moved Permanently', response_headers)
            response_headers.append(('Location', '/'))
            return ['Moved permanently: /']

        request_method = environ['REQUEST_METHOD'].lower()
        method_handlers = {
            'get': get_value,
            'put': set_value
        }
        return method_handlers[request_method](environ, start_response,
                                               response_headers, actor)\
            if request_method in method_handlers else return_405
    return application


class AbstractActor:
    def validate(self, value):
        assert value in self.value_range,\
            '{0} not in range {1}'.format(value, self.value_range)
        return int(value)


class Actor(AbstractActor):
    def __init__(self, value, value_range):
        self.value_range = value_range
        self.set_value(value)
    def set_value(self, new_value):
        self.value = self.validate(new_value)
    def get_value(self):
        return self.value


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='port', type=int, help="Port for server",
        default=9001)

    subparsers = parser.add_subparsers(
        help="please decide: 'a' for actor server mode or 'r' for actor controller?")

    actor_server = subparsers.add_parser('a', help='Start Actor server')
    actor_server.add_argument('-v', dest='value', action='store', type=int,
        default=0,
        help="Energy consumption alue for actor. Integer, positive or negative")
    actor_server.add_argument('--value-range', dest='value_range', action='append',
        help="Acceptable values for energy consumption of this actor server")

    actor_controller = subparsers.add_parser('r',
        help='Start actor as actor controller')
    actor_controller.add_argument('-a', dest='actors', action='append',
        help="URIs for remote actors of this controller actor actor")
    # TODO: -v?

    args = parser.parse_args()

    host_name = 'localhost'

    if args.value_range:
        value_range = [int(v) for v in args.value_range]
        assert args.value in value_range, 'please choose value from value_range'
        print value_range
    else:
        value_range = [args.value]

    if 'actors' in args:
        print "ActorOfRemoteActors"
        assert 0, 'please implement first'
        ActorOfRemoveActors = object
        actor = ActorOfRemoveActors(args.actors)
    else:
        print "Single Actor"
        actor = Actor(args.value, value_range)

    host_port_tuple = host_name, args.port
    host_uri = 'http://{0}:{1}'.format(*host_port_tuple)
    application = get_application(actor, host_uri)

    print "running server on port {0}".format(args.port)
    sock = eventlet.listen(host_port_tuple)
    try:
        eventlet.wsgi.server(sock, application, log=StringIO.StringIO())
    except (KeyboardInterrupt, SystemExit):
        print 'Server stopped.'
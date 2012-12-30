# -*- coding: utf-8 -*-
from __future__ import print_function

import json
from multiprocessing.process import Process
import socket

from smart_grid_actor.actor import ConnectionError


class Return400(Exception):
    pass
class Return500(Exception):
    pass

def return_301(start_response, response_headers):
    response_headers.append(('Content-Type', 'text/html'))
    response_headers.append(('Location', '/'))
    start_response('301 Moved Permanently', response_headers)
    return ['Moved permanently: /']

def return_405(start_response, response_headers, msg):
    response_headers.append(('Content-Type', 'text/html'))
    start_response('405 Method not allowed', response_headers)
    return [msg]

def return_406(start_response, response_headers, msg):
    response_headers.append(('Content-Type', 'text/html'))
    start_response('406 Not Acceptable', response_headers)
    return [msg]

def return_400(start_response, response_headers, msg):
    response_headers.append(('Content-Type', 'text/html'))
    start_response('400 Bad Request', response_headers)
    return [msg]

def return_500(start_response, response_headers, msg):
    response_headers.append(('Content-Type', 'text/html'))
    start_response('500 Internal Error', response_headers)
    return [msg]


def return_json_200(
        start_response,
        response_headers,
        output_dct
        ):
    output = json.dumps(output_dct)
    response_headers.append(
        ('Content-Type', 'application/json'))
    response_headers.append(
        ('Content-Length', str(len(output))))
    start_response('200 OK', response_headers)

    return [output]


def get_value_range(environ, actor):
    # convert set to list because list cannot be serialised
    return {'value_range': list(actor.get_value_range())}


def get_value(environ, actor):
    try:
        return {'value': actor.get_value()}
    except ConnectionError as exc:
        print("Error connecting to actor", exc.message)
        raise Return500("A subgrid participant did not respond")


def set_value(environ, actor):
    data = environ['wsgi.input'].read()
    try:
        actor.set_value(data)
    except actor.NotSolvable as exc:
        raise Return400("Input error: %s" % exc.message)
    except Exception as exc:
        raise Return400("Unknown Input error: %s" % exc)
    return get_value(environ, actor)


def get_wsgi_application(actor, host_uri, log_requests=None):
    url_map = {
        '/vr/': {
            'get': get_value_range,
            },
        '/': {
            'get': get_value,
            'put': set_value
        }
    }

    def application(environ, start_response):
        request_method = environ['REQUEST_METHOD'].lower()
        request_url = environ['PATH_INFO']

        if log_requests:
            import datetime
            now = datetime.datetime.strftime(
                datetime.datetime.now(),'%Y%m%d-%H%M%S')
            print(now, request_method, request_url)

        response_headers = [
            ('Host', host_uri),
            ('Content-Location', request_url)
        ]

        kw = dict(
            start_response=start_response,
            response_headers=response_headers,
        )

        if request_url in url_map.keys():
            method_handlers = url_map[request_url]
        else:
            return return_301(**kw)

        if 'HTTP_ACCEPT' in environ:
            if environ['HTTP_ACCEPT'] in [
                'text/json',
                'application/json',
                '*/*',
                ]:
                pass
            else:
                return return_406(
                    msg=('Wrong Accept header: only '
                         'text/json acceptable'),
                    **kw
                )

        if request_method in method_handlers:
            try:
                output_dct = method_handlers[request_method](
                    environ, actor)
                return return_json_200(
                    output_dct=output_dct, **kw
                )
            except Return400 as exc:
                return return_400(msg=exc.message, **kw)
            except Return500 as exc:
                return return_500(msg=exc.message, **kw)
        else:
            return return_405(
                msg=u'Allowed methods: {0}'.format(
                    u" ".join([m.upper()
                   for m in method_handlers.keys()])
                ),
                **kw
            )
    return application


def get_host_name(host_name_str):
    if host_name_str == "":
        try:
            host_name = socket.gethostbyname(
                socket.gethostname()
            )
        except socket.gaierror:
            tmp_conn = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM
            )
            try:
                tmp_conn.connect(("kit.edu", 80))
                host_name = tmp_conn.getsockname()[0]
                tmp_conn.close()
            except socket.gaierror:
                print("Cannot determine own hostname")
                host_name = host_name_str
    else:
        host_name = host_name_str
    return host_name


def start_bjoern_server(wsgi_application, host_name, port):
    import bjoern
    try:
        bjoern.run(wsgi_application, host_name, port)
    except KeyboardInterrupt:
        pass


def start_wsgiref_server(
        wsgi_application, host_name, port):
    from wsgiref.simple_server import make_server
    httpd = make_server(host=host_name,
        port=port, app=wsgi_application)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


def get_free_port(host_port_tuple):
    """ Returns a free port by binding a socket
    and closing it again
    """
    try:
        sock = socket.socket()
        sock.bind(host_port_tuple)
    except socket.error as (err_num, _err_str):
        if err_num == 48:
            raise Exception(
                ('Port "{0}" is already in use --> start '
                 'with "--exclude {0}"? --> Not starting '
                 'server on {0}.').format(host_port_tuple[1])
            )
        raise
    port = sock.getsockname()[1]
    sock.close()
    return port


def start_actor_server(
        actor,
        host_port_tuple=None,
        start_in_background_thread=False,
        log_requests=False,
        server_starter=start_bjoern_server
        ):
    if server_starter != start_bjoern_server:
        print("Using builtin server (slow)")

    if not host_port_tuple:
        # if no specific port is given,
        # run on free port
        host_port_tuple = ('', 0)

    port = host_port_tuple[1]
    if host_port_tuple[1] == 0:
        port = get_free_port(host_port_tuple)

    host_name = get_host_name(host_port_tuple[0])

    host_uri = 'http://{0}:{1}'.format(host_name, port)
    print("Running server on {0}".format(host_uri))

    wsgi_application = get_wsgi_application(
        actor, host_uri,
        log_requests=log_requests
    )

    if start_in_background_thread:
        process = Process(
            target=server_starter,
            args=(wsgi_application, host_name, port)
        )
        process.daemon = True
        process.start()
        return host_uri, process

    server_starter(wsgi_application, host_name, port)

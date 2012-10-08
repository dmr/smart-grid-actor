# -*- coding: utf-8 -*-
import json
import socket

import eventlet
import eventlet.wsgi

from smart_grid_actor.actor import ConnectionError


import multiprocessing
import multiprocessing.pool


# To bypass the "daemon-process not allowed to have
# child processes" restriction: introduce own Pool implementation
class NoDaemonProcess(multiprocessing.Process):
    # 'daemon' attribute should always return False
    _get_daemon = lambda self: False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)
# sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is a wrapper function, not a proper class.
class CustomPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


class Return400(Exception):
    pass
class Return500(Exception):
    pass

def return_301(start_response, response_headers):
    response_headers.append(('Content-Type', 'text/html'))

    # TODO: soll das so sein?
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


def return_json_200(start_response, response_headers,
                    output_dct):
    output = json.dumps(output_dct)
    response_headers.append(
        ('Content-Type', 'application/json'))
    response_headers.append(
        ('Content-Length', str(len(output))))
    start_response('200 OK', response_headers)

    return [output]


#def return_rdf_200(start_response, response_headers, output_dct):
#    dct_key_to_rdf_map = {
#        'value_range': 'https://example.com/Actor/value_range',
#        'value': 'https://example.com/Actor/value',
#    }
#    assert 0, 'implement'


def get_value_range(environ, actor):
    # convert set to list because list cannot be serialised
    return {'value_range': list(actor.get_value_range())}


def get_value(environ, actor):
    try:
        return {'value': actor.get_value()}
    except ConnectionError as exc:
        print "Error connecting to actor",exc.message
        raise Return500("A subgrid participant did not respond")

def set_value(environ, actor):
    data = environ['wsgi.input'].read()

    try:
        actor.set_value(data)
    except actor.NotSolvable as exc:
        print exc
        raise Return400("Input error: %s" % exc.message)
    except Exception as exc:
        raise Return400("Unknown Input error: %s" % exc)

    return get_value(environ, actor)


def get_application(actor, host_uri):

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
                # TODO: negotiate more?
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
                return return_json_200(output_dct=output_dct, **kw)
            except Return400 as exc:
                return return_400(msg=exc.message, **kw)
            except Return500 as exc:
                return return_500(msg=exc.message, **kw)
        else:
            return return_405(msg=u'Allowed methods: {0}'.format(
                u" ".join([m.upper() for m in method_handlers.keys()])),
                **kw
            )
    return application


def start_actor_server(
        actor,
        host_port_tuple=None,
        start_in_background_thread=False,
        log_to_std_err=False
        ):

    if not host_port_tuple:
        # if no specific port is given,
        # run on free port
        host_port_tuple = ('localhost', 0)

    try:
        sock = eventlet.listen(host_port_tuple)
    except socket.error as (err_num, err_str):
        if err_num == 48:
            print ('Port "{0}" is already in use --> start '
                'with "--exclude {0}"? --> Not starting '
                'server on {0}.').format(host_port_tuple[1])
            import sys
            sys.exit(1)
        raise

    port = sock.getsockname()[1]

    host_uri = 'http://{0}:{1}'.format(host_port_tuple[0], port)
    print "Running actor server on {0}".format(host_uri)

    application = get_application(actor, host_uri)

    if log_to_std_err:
        logger = None
    else:
        import StringIO
        logger = StringIO.StringIO()

    if start_in_background_thread == True:
        process = NoDaemonProcess(
            target=eventlet.wsgi.server,
            args=(sock, application),
            kwargs=dict(log=logger)
        )
        process.daemon = True
        process.start()
        return port, process
    else:
        try:
            eventlet.wsgi.server(
                sock, application,
                log=logger
            )
        except (KeyboardInterrupt, SystemExit):
            print 'Server stopped.'
            raise

# -*- coding: utf-8 -*-

import socket
import eventlet
import eventlet.wsgi


def get_value_range(environ, start_response, response_headers, actor):

    # convert set to list because list cannot be serialised
    actor_vr = list(actor.get_value_range())

    output = json.dumps({'value_range': actor_vr})
    response_headers.append(('Content-Type', 'application/json'))
    response_headers.append(('Content-Length', str(len(output))))
    start_response('200 OK', response_headers)
    return [output]


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

        #if serialization=='rdf':
        #    response_headers.append(('Content-type', 'text/n3'))
        #    assert 0, "implement"
        # #output = data_generator.data_to_serialized_graph(**kw)
        #if 'HTTP_ACCEPT' in environ and
        #    not environ['HTTP_ACCEPT'] == 'text/json':
        #    start_response('406 Not Acceptable', response_headers)
        #    return ['Wrong Accept header: only text/json acceptable']
        #if 'HTTP_ACCEPT_ENCODING' in environ:
        # 'identity, deflate, compress, gzip' --> ?

        request_method = environ['REQUEST_METHOD'].lower()

        response_headers = [('Host', host_uri),
            ('Content-Location', environ['PATH_INFO'])]

        if environ['PATH_INFO'] == '/vr/':
            method_handlers = {
                'get': get_value_range,
            }
        elif environ['PATH_INFO'] == '/':
            method_handlers = {
                'get': get_value,
                'put': set_value
            }
        else:
            start_response('301 Moved Permanently', response_headers)
            response_headers.append(('Location', '/'))
            return ['Moved permanently: /']

        return method_handlers[request_method](environ, start_response,
                                               response_headers, actor)\
            if request_method in method_handlers else return_405
    return application


def start_actor_server(host_port_tuple, actor,
                       start_in_background_thread=False
    ):
    host_uri = 'http://{0}:{1}'.format(*host_port_tuple)

    print "Running actor server on {0}".format(host_uri)
    try:
        sock = eventlet.listen(host_port_tuple)
    except socket.error as (err_num, err_str):
        if err_num == 48:
            print ('Port "{0}" is already in use --> start with "--exclude'
                   '{0}"? --> Not starting server on {0}.').format(port)
        raise

    application = get_application(actor, host_uri)

    if start_in_background_thread == True:
        import StringIO

        from simulation import NoDaemonProcess
        process = NoDaemonProcess(
            target=eventlet.wsgi.server,
            args=(sock, application),
            kwargs=dict(log=StringIO.StringIO())
        )
        process.daemon = True
        process.start()

    else:
        try:
            eventlet.wsgi.server(sock, application)
        except (KeyboardInterrupt, SystemExit):
            print 'Server stopped.'
            raise

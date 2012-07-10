#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time

import argparse

import eventlet
import eventlet.wsgi
import threading, StringIO


from actor_server import Actor, get_application


def get_start_number_exclude_parser_results():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host-name', action="store", default='localhost',
                        type=str, help="First server's port")

    parser.add_argument('-s','--start_port', action="store", default=9000,
                        type=int, help="First server's port")
    parser.add_argument('-e', '--exclude', action="append",
                        type=int, help='Exclude ports')

    parser.add_argument('-n','--number', action="store", default=4496,
                        type=int, help='Start n servers')

    argparse_results = parser.parse_args()

    port_range = range(argparse_results.start_port,
                       argparse_results.start_port+argparse_results.number)
    if argparse_results.exclude:
        for exclude_port in argparse_results.exclude:
            if exclude_port in port_range:
                port_range.append(max(port_range)+1)
                port_range.remove(exclude_port)
        print "Starting {0} servers: {1} --> {2}. excluded {3}".format(
            len(port_range), min(port_range), max(port_range),
            ', '.join(str(e) for e in argparse_results.exclude))
    else:
        print "Starting {0} servers: {1} --> {2}".format(
            len(port_range),min(port_range),max(port_range))

    return argparse_results.host_name, port_range


if __name__ == '__main__':
    host_name, port_range = get_start_number_exclude_parser_results()

    eventlet.monkey_patch(all=True)


    # TODO: random?
    actor_value = 2
    actor_val_lst = [0,2,1]

    for i, port in enumerate(port_range):
        try:
            host_port_tuple = host_name, port
            sock = eventlet.listen(host_port_tuple)
        except socket.error as (err_num, err_str):
            if err_num == 48:
                print ('Port "{0}" is already in use --> start with "--exclude'
                       '{0}"? --> Not starting server on {0}.').format(port)
            raise

        host_uri = 'http://{0}:{1}'.format(*host_port_tuple)
        print "Running actor server on {0}".format(host_uri)

        actor = Actor(actor_value, actor_val_lst)

        application = get_application(actor, host_uri)

        thr = threading.Thread(target=eventlet.wsgi.server,
                               args=(sock, application),
                               kwargs=dict(log=StringIO.StringIO())
        )
        thr.daemon = True
        thr.start()

    try:
        print "I am done starting. Now wait."
        while True: time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print "Exiting..."

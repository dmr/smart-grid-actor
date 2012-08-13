#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import time
import urllib2

count = 0


def get_actor_value(actor):
    time_before_request = time.time()
    actor_value = actor.get_value()
    time_after_request = time.time()
    return time_before_request, time_after_request, actor_value


def parallel_query_actors(actors,
        worker_count=4, # optimum for worker count with two processors
        callback=lambda v:v):
    pool = multiprocessing.Pool(processes=worker_count)
    try:
        result = pool.map_async(get_actor_value, actors, callback=callback)
        pool.close()
        pool.join()
    except (KeyboardInterrupt, SystemExit):
        print 'parent received control-c'
        pool.terminate()
        raise
    except Exception:
        pool.terminate()
        raise
    return result


class AbstractActor(object):
    def __repr__(self):
        return u"<{0}: {1}>".format(self.__class__.__name__, self.id)
    def __init__(self):
        # global actor count
        global count
        count +=1
        self.id = count
    def validate(self, value):
        value_range = self.get_value_range()
        assert value in value_range,\
            '{0} not in value_range {1}'.format(value, value_range)
        return int(value)


class Actor(AbstractActor):
    def __init__(self, value, value_range,
                 value_delay=float(.03)
    ):
        self.value_range = value_range
        self.set_value(value)
        self.value_delay = value_delay

    def get_value(self):
        time_before_request = time.time()
        #time.sleep(self.value_delay)
        time_after_request = time.time()
        return self.value

    def get_value_range(self):
        return self.value_range
    def set_value(self, new_value):
        self.value = self.validate(new_value)


class ControllerActor(AbstractActor):
    def __init__(self, actors):
        for a in actors:
            assert isinstance(a, AbstractActor)
        self.actors = actors
    def get_value(self):
        time_before_request = time.time()
        query_results = parallel_query_actors(self.actors)
        print "res"
        import pprint; pprint.pprint(query_results)
        time_after_request = time.time()
        result = str(sum([int(body) for _t, _t, body in query_results]))
        time_after_calculation = time.time()
        return result

    def set_value(self, new_value):
        raise NotImplementedError('Setting a value of a Controller actor not implemented yet.')
        #self.value = self.validate(new_value)


class RemoteActor(AbstractActor):
    def __init__(self, uri):
        self.uri = uri
    def get_value(self):
        timeout = 5
        try:
            time_before_request = time.time()
            request_result = urllib2.urlopen(self.uri, timeout=timeout).read()
            time_after_request = time.time()
        except Exception as e:
            # show error in multiprocessing process also
            print "Error querying {0}".format(self.uri)
            import traceback; print traceback.format_exc()
            raise
        return request_result

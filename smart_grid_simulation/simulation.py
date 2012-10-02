# -*- coding: utf-8 -*-
import multiprocessing
import multiprocessing.pool
import time
import urllib2
import json

import csp_solver


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


count = 0


class NotSolvable(Exception):
    pass


def get_actor_value(actor):
    time_before_request = time.time()
    actor_value = actor.get_value()
    time_after_request = time.time()
    return time_before_request, time_after_request, actor_value


def parallel_query_actors(
        actors,
        worker_count=4, # optimum for worker count with two processors
        fct=get_actor_value
        ):
    pool = CustomPool(processes=worker_count)
    try:
        result = pool.map_async(fct, actors)
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
    NotSolvable = NotSolvable

    def log(self, msg): print time.time(), self.id, msg

    def __repr__(self):
        return u"<{0}: {1}>".format(self.__class__.__name__, self.id)

    def __init__(self):
        # global actor count
        global count
        count +=1
        self.id = count

    def get_value_range(self):
        raise NotImplementedError()
    def get_value(self):
        raise NotImplementedError()
    def set_value(self, new_value):
        raise NotImplementedError()

    def __eq__(self, other):
        # Two Actors are equal if share the same
        # value range and current value
        if not type(other) == type(self): return False
        if not self.get_value_range() == other.get_value_range():
            return False
        if not self.get_value() == other.get_value():
            return False
        return True
    def __ne__(self, other):
        if type(other) != type(self): return True
        if not self.get_value_range() == other.get_value_range():
            return True
        if not self.get_value() == other.get_value():
            return True
        return False

    def __hash__(self):
        # It is wrong to really compare the object here.
        # __hash__ is used for comparisons if two objects
        # mean the same object
        return hash(self.id)

    def validate(self, value):
        try:
            set_value = int(value)
        except ValueError as exc:
            raise NotSolvable(
                "Not a valid integer: '%s'" % value)
        if set_value != value:
            self.log("Value was converted: %s --> %s"
                % (value, set_value))
        return set_value


class Actor(AbstractActor):
    _value_range = None
    _value = None

    def __init__(self,
                 value_range,
                 value=None
                 ):
        for val in value_range:
            if not int(val) == val:
                raise ValueError('Invalid value_range: '
                    'Not an integer value: "%s"' % val)

        self._value_range = set(value_range)

        AbstractActor.__init__(self)

        if value is not None:
            try:
                self.set_value(value)
            except NotSolvable as exc:
                raise ValueError(exc.message)
        else:
            # assumption: if no value is given, consume as little
            # as possible
            self.set_value(min(self._value_range))

    def get_configuration(self):
        return dict(
            id=self.id,
            value_range=self._value_range,
            value=self._value,
            cls=self.__class__.__name__
        )

    def get_value(self):
        return self._value

    def get_value_range(self):
        return self._value_range

    def set_value(self, new_value):
        set_value = self.validate(new_value)

        value_range = self.get_value_range()
        if not set_value in value_range:
            raise NotSolvable(
                '{0} not in value_range {1}'.format(
                    set_value, list(value_range)))

        self._value = set_value
        return set_value

class ControllerActor(AbstractActor):
    _actors=None

    def __init__(self,
                 actors,
                 csp_solver_config
    ):
        for actor in actors:
            if not isinstance(actor, AbstractActor):
                raise Exception("Please pass a valid "
                    "AbstractActor instance, not '%s'"
                    % actor
                )
        # actors needs to be a list
        assert isinstance(actors, list)
        self._actors = actors
        AbstractActor.__init__(self)

        self._csp_solver_config = csp_solver_config

    def get_configuration(self):
        return dict(
            id=self.id,
            actors=[actor.get_configuration()
                    for actor in self._actors],
            cls=self.__class__.__name__
        )

    def get_value(self):
        #time_before_request = time.time()
        query_results = parallel_query_actors(
            self._actors)
        #time_after_request = time.time()
        query_results.wait()
        result = sum([
            int(body)
            for _t, _t, body in query_results.get()
        ])
        time_after_calculation = time.time()
        return result

    def get_value_range(self):
        # alternative algorithm: try every possible answer. This is
        # not an option as there might be infinity possibilities
        # --> calculate a few small problems by trying out every
        # possibility is solvable and faster

        range_min = 0
        range_max = 0
        all_actor_ranges = []

        for actor in self._actors:
            actor_value_range = actor.get_value_range()
            all_actor_ranges.append(actor_value_range)
            actor_min = min(actor_value_range)
            range_min += actor_min
            actor_max = max(actor_value_range)
            range_max += actor_max

        range_theo_max = range(range_min, range_max+1)
        range_theo_max_length = len(range_theo_max)

        if range_theo_max_length > 500:
            self.log('warning: big interval to check: {0}'.format(
                range_theo_max_length))
            raise ValueError('please improve algorithm for large numbers')

        own_value_range = set()

        for possibly_a_value_range_value in range_theo_max:
            #self.log('trying to find {0}'.format(result))
            csp_result = csp_solver.do_solve(
                variables=all_actor_ranges,
                reference_value=possibly_a_value_range_value,
                csp_solver_config=self._csp_solver_config
            )

            #problem = constraint.Problem(self._solver)
            ## HACK: knowledge of constraint's datastructure to avoid copy
            #assert not problem._variables
            #problem._variables = variables
            ##for id, domain in variables.items():
            ##    problem.addVariable(id, domain)
            ## HACK until here
            ##problem.addConstraint(
            # constraint.ExactSumConstraint(result), variables.keys())
            #problem.addConstraint(
            # lambda *vars: sum(vars) == result, variables.keys())
            #self.log('solving problem')
            #solution = problem.getSolution()

            if ('satisfiable_bool' in csp_result
                and csp_result['satisfiable_bool'] == True):
                own_value_range.add(possibly_a_value_range_value)
            else:
                self.log('not a solution: {0}'.format(
                    possibly_a_value_range_value))

        return own_value_range

    def set_value(self, new_value):
        set_value = self.validate(new_value)

        all_actor_ranges = []
        for actor in self._actors:
            actor_value_range = actor.get_value_range()
            all_actor_ranges.append(actor_value_range)

        csp_result = csp_solver.do_solve(
            variables=all_actor_ranges,
            reference_value=set_value,
            csp_solver_config=self._csp_solver_config
        )

        if ('satisfiable_bool' in csp_result
            and csp_result['satisfiable_bool'] == True):

            for index, assigned_value in enumerate(csp_result['solution_list']):
                self.log('Setting value %s for Actor %s (id %s)'
                         % (assigned_value, index, self._actors[index]))
                self._actors[index].set_value(assigned_value)

            #self.set_value_time = time.time()

            return set_value

        else:
            raise NotSolvable(
                '{0} is not an satisfiable'.format(set_value)
            )


class RemoteActor(AbstractActor):
    _uri = None

    def __init__(self, uri, get_timeout=5):
        self._uri = uri
        self.get_timeout = get_timeout
        AbstractActor.__init__(self)

    def get_configuration(self):
        return dict(
            id=self.id,
            uri=self._uri,
            cls=self.__class__.__name__
        )

    def get_value(self):
        try:
            #time_before_request = time.time()
            url = self._uri + '/'
            request_result = urllib2.urlopen(url,
                timeout=self.get_timeout).read()
            #time_after_request = time.time()
        except urllib2.URLError as exc:
            raise urllib2.URLError(
                '{0} {1}'.format(self._uri, exc.reason))

        except Exception as exc:
            # show error in multiprocessing process also
            print "Error querying {0}".format(self._uri)
            import traceback; print traceback.format_exc()
            raise

        actor_value = json.loads(request_result)['value']
        return actor_value

    def get_value_range(self):
        try:
            #time_before_request = time.time()
            url = self._uri + '/vr/'
            request_result = urllib2.urlopen(url,
                timeout=self.get_timeout).read()
            #time_after_request = time.time()
        except urllib2.HTTPError as exc:
            raise NotSolvable('400 %s' % exc)
        except urllib2.URLError as exc:
            raise urllib2.URLError(
                '{0} {1}'.format(self._uri, exc.reason))

        except Exception as exc:
            # show error in multiprocessing process also
            #print "Error querying {0}".format(self.uri)
            #import traceback; print traceback.format_exc()
            raise

        actor_value_range = set(
            json.loads(request_result)['value_range']
        )
        return actor_value_range

    def set_value(self, new_value):
        set_value = self.validate(new_value)

        try:
            #time_before_request = time.time()
            url = self._uri + '/'
            data = str(set_value)
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(url, data=data)
            request.add_header('Content-Type', 'application/json')
            request.get_method = lambda: 'PUT'
            request_response = opener.open(
                request, timeout=self.get_timeout)
            request_result = request_response.read()
            #time_after_request = time.time()
        except urllib2.HTTPError as exc:
            raise NotSolvable('400 %s' % exc)
        except urllib2.URLError as exc:
            raise urllib2.URLError(
                '{0} {1}'.format(self._uri, exc.reason))

        except Exception as exc:
            # show error in multiprocessing process also
            #print "Error querying {0}".format(self.uri)
            #import traceback; print traceback.format_exc()
            raise

        actor_value = json.loads(request_result)['value']
        return actor_value

# -*- coding: utf-8 -*-

import multiprocessing
import time
import urllib2

import csp_solver
minisat_path = '/Users/daniel/Desktop/DA/code/minisat'
sugarjar_path = '/Users/daniel/Desktop/DA/code/sugar-v1-15-0.jar'

import tempfile
tmp_folder = tempfile.gettempdir()



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
        #callback=lambda v:v
        ):
    pool = multiprocessing.Pool(processes=worker_count)
    try:
        result = pool.map_async(fct, actors) #, callback=callback)
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
        # It is wrong to really compare the object here. This case is
        # important to work with references in set() instances for instance
        return hash(self.id)

    def validate(self, value):
        value_range = self.get_value_range()
        if not value in value_range:
            raise NotImplementedError(
            '{0} not in value_range {1}'.format(value, value_range))
        return int(value)


class Actor(AbstractActor):
    def __init__(self, value, value_range,
                 value_delay=float(.03)
    ):
        self.value_range = value_range
        self.set_value(value)
        self.value_delay = value_delay
        AbstractActor.__init__(self)

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
        AbstractActor.__init__(self)

    def get_value(self):
        time_before_request = time.time()
        query_results = parallel_query_actors(
            self.actors)
        print "res"
        import pprint; pprint.pprint(query_results)
        time_after_request = time.time()
        result = str(sum([int(body) for _t, _t, body in query_results]))
        time_after_calculation = time.time()
        return result

    def get_value_range(self):
        range_min = 0
        range_max = 0
        all_actor_ranges = []

        for actor in self.actors:
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
            assert 0, 'please improve algorithm for large numbers'

        # faster to calculate a few small problems that to run through
        # every possible answer (--> infinity)
        own_value_range = []

        #import ramdisk_mounter
        #with ramdisk_mounter.ramdisk(tmp_folder):
        for possibly_a_value_range_value in range_theo_max:
            #self.log('trying to find {0}'.format(result))
            csp_result = csp_solver.do_solve(
                variables=all_actor_ranges,
                reference_value=possibly_a_value_range_value,
                tmp_folder=tmp_folder,
                minisat_path=minisat_path,
                sugarjar_path=sugarjar_path
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
                own_value_range.append(possibly_a_value_range_value)
            else:
                self.log('not a solution: {0}'.format(
                    possibly_a_value_range_value))

        return own_value_range

    def set_value(self, new_value):
        value_range = self.get_value_range()

        #import ramdisk_mounter
        #with ramdisk_mounter.ramdisk(tmp_folder):
        csp_result = csp_solver.do_solve(
            variables=value_range,
            reference_value=new_value,
            tmp_folder=tmp_folder,
            minisat_path=minisat_path,
            sugarjar_path=sugarjar_path
        )
        if ('satisfiable_bool' in csp_result
            and csp_result['satisfiable_bool'] == True):
            for index, assigned_value in enumerate(csp_result['solutions']):
                self.log('Setting value %s for Actor %s (id %s)'
                         % (assigned_value, index, self.actors[index]))
                self.actors[index].set_value(assigned_value)

            self._value_setpoint = new_value # this should be the new value
            self.set_value_time = time.time()
        else:
            raise NotSolvable('{0} not in {1}'.format(new_value,
                                                      value_range))

        #self.value = self.validate(new_value)


class RemoteActor(AbstractActor):
    def __init__(self, uri, get_timeout=5):
        self.uri = uri
        self.get_timeout = get_timeout
        AbstractActor.__init__(self)

    def get_value(self):
        try:
            time_before_request = time.time()
            request_result = urllib2.urlopen(self.uri,
                timeout=self.get_timeout).read()
            time_after_request = time.time()
        except Exception as e:
            # show error in multiprocessing process also
            print "Error querying {0}".format(self.uri)
            import traceback; print traceback.format_exc()
            raise
        return request_result

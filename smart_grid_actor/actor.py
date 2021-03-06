# -*- coding: utf-8 -*-
from __future__ import print_function
import time


class ConfigurationException(Exception):
    pass

USED_IDS = set([])

def get_next_free_id(id_collection):
    assert isinstance(id_collection, set)
    return max(id_collection) + 1 if id_collection else 1

def register_id(identifier, id_collection):
    if identifier:
        new_id = int(identifier)
        if new_id in id_collection:
            raise ConfigurationException(
                "Id {0} already taken".format(new_id)
            )
    else:
        new_id = get_next_free_id(id_collection)
    id_collection.add(new_id)
    return new_id


class NotSolvable(Exception):
    pass
class ConnectionError(Exception):
    pass


class AbstractActor(object):
    NotSolvable = NotSolvable

    def log(self, msg):
        print(time.time(), self.id, msg)

    def __repr__(self):
        return u"<{0}: {1}>".format(
            self.__class__.__name__, self.id)

    def __init__(
            self,
            id=None,
            id_collection=None,
            level=None,
            ):
        self.id = register_id(
            identifier=id,
            id_collection=id_collection if id_collection else USED_IDS
        )

        if level:
            self.level = level

    def get_value_range(self):
        raise NotImplementedError()
    def get_value(self):
        raise NotImplementedError()
    def set_value(self, new_value):
        raise NotImplementedError()

    def __eq__(self, other):
        # Two Actors are equal if they share the same
        # value range and current value
        if not type(other) == type(self):
            return False
        if not self.get_value_range() == other.get_value_range():
            return False
        if not self.get_value() == other.get_value():
            return False
        return True
    def __ne__(self, other):
        if type(other) != type(self):
            return True
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
        except ValueError:
            raise NotSolvable(u"Not a valid integer: '{0}'".format(value))
        if set_value != value:
            self.log(u"Value was converted: {0} --> {1}".format(
                value, set_value))
        return set_value


class Actor(AbstractActor):
    _value_range = None
    _value = None

    def __init__(
            self,
            value_range,
            value=None,
            **kwargs
            ):
        for val in value_range:
            if not int(val) == val:
                raise ValueError('Invalid value_range: '
                    'Not an integer value: "{0}"'.format(val))

        self._value_range = set(value_range)

        AbstractActor.__init__(self, **kwargs)

        if value is not None:
            try:
                self.set_value(value)
            except NotSolvable as exc:
                raise ValueError(exc.message)
        else:
            # assumption: if no value is given,
            # consume as little as possible
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

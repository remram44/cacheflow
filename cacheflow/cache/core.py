import cloudpickle
from hashlib import sha256

from .base import Cache


class NullCache(Cache):
    """Dumb cache that doesn't store anything.
    """
    def has_key(self, key):
        return False

    def retrieve(self, key):
        raise KeyError(key)

    def store(self, key, value, work_amount=None):
        pass


class MemoryCache(Cache):
    """In-memory cache that simply stores everything in a dict.
    """
    def __init__(self):
        self.store = {}

    def has_key(self, key):
        return key in self.store

    def retrieve(self, key):
        return self.store[key]

    def store(self, key, value, work_amount=None):
        self.store[key] = value


class HashFileWrapper(object):
    def __init__(self, h):
        self.h = h

    def write(self, b):
        self.h.update(b)

    def flush(self):
        pass

    def close(self):
        pass


def hash_value(value):
    h = sha256()
    cloudpickle.dump(value, HashFileWrapper(h))
    return h.hexdigest()

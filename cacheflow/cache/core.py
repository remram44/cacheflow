import cloudpickle
import contextlib
from hashlib import sha256
import os
import re

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


class DirectoryCache(Cache):
    """On-disk cache that writes to files in a directory.
    """
    def __init__(self, directory):
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self.directory = directory

    _path_re = re.compile(r'[^A-Za-z0-9-]')

    def _path(self, key):
        assert isinstance(key, tuple)
        return os.path.join(self.directory, '__'.join(
            self._path_re.sub(lambda m: '_%x' % ord(m.group(0)), k)
            for k in key
        ))

    def has_key(self, key):
        return os.path.exists(self._path(key))

    def retrieve(self, key):
        stack = contextlib.ExitStack()
        with stack:
            try:
                fp = stack.enter_context(open(self._path(key), 'rb'))
            except FileNotFoundError:
                raise KeyError(key)
            return cloudpickle.load(fp)

    def store(self, key, value, work_amount=None):
        with open(self._path(key), 'wb') as fp:
            cloudpickle.dump(value, fp)


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

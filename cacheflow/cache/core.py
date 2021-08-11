import cloudpickle
import contextlib
import copyreg
from hashlib import sha256
import io
import os
import pickle
import re
import tempfile

from .base import Cache


class NullCache(Cache):
    """Dumb cache that doesn't store anything.
    """
    def has_key(self, key):
        return False

    def retrieve(self, key, **kwargs):
        raise KeyError(key)

    def store(self, key, value, **kwargs):
        pass


class MemoryCache(Cache):
    """In-memory cache that simply stores everything in a dict.
    """
    def __init__(self):
        self.store = {}

    def has_key(self, key):
        return key in self.store

    def retrieve(self, key, **kwargs):
        return self.store[key]

    def store(self, key, value, **kwargs):
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

    def retrieve(self, key, pickling, **kwargs):
        stack = contextlib.ExitStack()
        with stack:
            try:
                fp = stack.enter_context(open(self._path(key), 'rb'))
            except FileNotFoundError:
                raise KeyError(key)
            return pickling.load(fp)

    def store(self, key, value, pickling, **kwargs):
        with open(self._path(key), 'wb') as fp:
            try:
                pickling.dump(value, fp)
                return
            except TypeError:
                pass
        os.remove(self._path(key))


class HashFileWrapper(object):
    def __init__(self, h):
        self.h = h

    def write(self, b):
        self.h.update(b)

    def flush(self):
        pass

    def close(self):
        pass


class _Unhashable(object):
    def __hash__(self):
        raise TypeError

    def __eq__(self, other):
        return False

    def __neq__(self, other):
        return True


UNHASHABLE = _Unhashable()


def hash_value(value, pickling):
    h = sha256()
    try:
        pickling.dump(value, HashFileWrapper(h))
    except TypeError:
        return UNHASHABLE
    return h.hexdigest()


class TemporaryFile(object):
    def __init__(self, temp_dir, suffix=None):
        fd, self.name = tempfile.mkstemp(dir=temp_dir, suffix=suffix)
        os.close(fd)

    def __getstate__(self):
        with open(self.name, 'rb') as fp:
            return {'contents': fp.read()}

    def __setstate__(self, state):
        with open(self.name, 'wb') as fp:
            fp.write(state['contents'])


class Pickler(cloudpickle.CloudPickler):
    def __init__(self, file, *, temp_dir):
        super(Pickler, self).__init__(file, protocol=4)
        self.__temp_dir = temp_dir

        if hasattr(self, 'dispatch_table'):
            pass
        elif hasattr(self, 'dispatch'):
            self.dispatch_table = self.dispatch.copy()
        else:
            self.dispatch_table = copyreg.dispatch_table.copy()
        self.dispatch_table[TemporaryFile] = self._tempfile_reduce

    def _tempfile_reduce(self, obj):
        name = os.path.basename(obj.name)
        if '.' in name:
            suffix = '.' + name.split('.', 1)[1]
        else:
            suffix = None
        with open(obj.name, 'rb') as fp:
            contents = fp.read()
        return type(obj), (suffix, contents)


class Unpickler(pickle.Unpickler):
    def __init__(self, file, *, temp_dir):
        super(Unpickler, self).__init__(file)
        self.__temp_dir = temp_dir

    def find_class(self, module, name):
        if (module, name) == (__name__, 'TemporaryFile'):
            return self._tempfile_builder
        return super(Unpickler, self).find_class(module, name)

    def _tempfile_builder(self, *args):
        suffix, contents = args
        obj = TemporaryFile(temp_dir=self.__temp_dir, suffix=suffix)
        with open(obj.name, 'wb') as fp:
            fp.write(contents)
        return obj


class Pickling(object):
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir

    def dump(self, obj, file):
        Pickler(file, temp_dir=self.temp_dir).dump(obj)

    def dumps(self, obj):
        buffer = io.BytesIO()
        Pickler(buffer, temp_dir=self.temp_dir).dump(obj)
        return buffer.getvalue()

    def load(self, file):
        return Unpickler(file, temp_dir=self.temp_dir).load()

    def loads(self, s):
        buffer = io.BytesIO(s)
        return Unpickler(buffer, temp_dir=self.temp_dir).load()

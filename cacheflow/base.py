class Cache(object):
    """Cache system, storing data for later retrieval.
    """
    def has_key(self, key):
        """Indicates whether a value is in the cache.
        """
        raise NotImplementedError

    def get(self, key):
        """Gets a value from the cache.
        """
        raise NotImplementedError

    def store(self, key, value):
        """Stores a new value to the cache.
        """
        raise NotImplementedError


class NullCache(Cache):
    """Dumb cache that doesn't store anything.
    """
    def has_key(self, key):
        return False

    def get(self, key):
        raise KeyError(key)

    def store(self, key, value):
        pass


class MemoryCache(Cache):
    """In-memory cache that simply stores everything in a dict.
    """
    def __init__(self):
        self.store = {}

    def has_key(self, key):
        return key in self.store

    def get(self, key):
        return self.store[key]

    def store(self, key, value):
        self.store[key] = value


class Module(object):
    """A module, as provided by a `ModuleLoader`.
    """
    def __call__(self, inputs, output_names, **kwargs):
        """Run on the inputs to provide outputs.
        """
        raise NotImplementedError


class ModuleLoader(object):
    """Module loader, capable of providing modules used by workflow steps.
    """
    def get_module(self, module):
        """Returns a module or None.
        """
        raise NotImplementedError

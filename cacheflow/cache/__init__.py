from .base import Cache
from .core import NullCache, MemoryCache, DirectoryCache, \
    Pickling, TemporaryFile, hash_value


__all__ = [
    'Cache', 'NullCache', 'MemoryCache', 'DirectoryCache',
    'Pickling', 'TemporaryFile', 'hash_value',
]


class SmartCache(Cache):
    """Smart cache, deciding whether to store data or not.

    A decision to store inputs or not is made depending on:

      * The value's size
      * The computational cost of re-computing the value
      * How often/recently the value was requested from the cache
    """
    def __init__(self, store):
        self.store = store

    def has_key(self, key):
        return self.store.has_key(key)

    def retrieve(self, key, **kwargs):
        value = self.store.retrieve(key, **kwargs)
        # TODO: Note that this key is popular
        return value

    def store(self, key, value, work_amount=None, **kwargs):
        # TODO: Decide whether to store
        # TODO: Need additional metadata to decide whether to store (deps)
        self.store.store(key, value, work_amount=work_amount, **kwargs)

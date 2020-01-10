from .base import Cache
from .core import NullCache, MemoryCache, DirectoryCache


class SmartCache(Cache):
    """Smart cache, deciding whether to store data or not.

    A decision to store inputs or not is made depending on:

      * 
    """
    def __init__(self, store):
        self.store = store

    def has_key(self, key):
        return self.store.has_key(key)

    def retrieve(self, key):
        value = self.store.retrieve(key)
        # TODO: Note that this key is popular
        return value

    def store(self, key, value, work_amount=None):
        # TODO: Decide whether to store
        # TODO: Need additional metadata to decide whether to store (deps)
        self.store.store(key, value, work_amount=work_amount)

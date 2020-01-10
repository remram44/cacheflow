class Cache(object):
    """Cache system, storing data for later retrieval.
    """
    # TODO: Figure out actual interface for this
    def has_key(self, key):
        """Indicates whether a value is in the cache.
        """
        raise NotImplementedError

    def retrieve(self, key):
        """Gets a value from the cache.
        """
        raise NotImplementedError

    def store(self, key, value, work_amount=None):
        """Stores a new value to the cache.
        """
        raise NotImplementedError

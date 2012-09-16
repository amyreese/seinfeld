import memcache
import pickle

from core import app

host = app.config['MC_URI']
mc = memcache.Client([host])

class mcdict(dict):
    """Memcache-backed dictionary."""

    def __new__(cls, key, *args, **kwargs):
        obj = mc.get(key)
        if obj is None:
            t = type('mcdict', (dict,), {})
            obj = t(*args, **kwargs)
            obj.__class__ = cls
            return obj

        else:
            obj = pickle.loads(obj)
            if type(obj) != mcdict:
                raise Exception('mc key {} already in use by non-mcdict value')
            return obj

    def __init__(self, key, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__key = key

    def __save(self):
        mc.set(self.__key, pickle.dumps(self))

    def __repr__(self):
        return '<mcdict {0}: {1}>'.format(self.__key, dict.__repr__(self))

    ### dict modify method mappings ###

    def __setitem__(self, key, value):
        rv = dict.__setitem__(self, key, value)
        self.__save()
        return rv

    def __delitem__(self, key):
        rv = dict.__delitem__(self, key)
        self.__save()
        return rv

    def update(self, *args, **kwargs):
        rv = dict.update(self, *args, **kwargs)
        self.__save()
        return rv

    def setdefault(self, key, value=None):
        rv = dict.setdefault(self, key, value)
        self.__save()
        return rv

def cache_method(self):
    mc.set(self._mc_key, pickle.dumps(self))

def flush_method(self):
    mc.delete(self._mc_key)

class Cacheable(type):
    """Metaclass for creating Memcached-backed objects.
    This injects a .cache() and .flush() method into the class definition,
    and will automatically load cached objects from the database when creating
    new objects.  Requires the class to derive from object, and requires the
    first parameter to __init__ to be the object's unique lookup key.

    Example:

        class Something(object):
            __metaclass__ = Cacheable

            def __init__(self, key, foo=True):
                self.foo = foo

        # create brand-new Something
        s = Something('new-key', foo='foo')

        # cache the new object
        s.cache()

        # pull the existing object from cache
        s2 = Something('new-key')

        # inspect the object
        print s2.foo # 'foo'

        # remove the object/key from cache
        s2.flush()

    """
    def __new__(meta, classname, bases, attrs):
        attrs['cache'] = cache_method
        attrs['flush'] = flush_method
        return type.__new__(meta, classname, bases, attrs)

    def __call__(cls, key, *args, **kwargs):
        classname = cls.__name__
        mc_key = '{}-{}'.format(classname.lower(), key)

        obj = mc.get(mc_key)
        if obj is None:
            obj = cls.__new__(cls)
            obj._mc_key = mc_key
            obj.__init__(key, *args, **kwargs)
            return obj

        else:
            obj = pickle.loads(obj)
            if type(obj) != cls:
                raise Exception('mc key {} already in use by non-{} value'.format(mc_key, classname))
            return obj

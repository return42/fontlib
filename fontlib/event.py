# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""Simple event & handler implementation.

.. hint::

   Most of the class EventHandler was copied from `Marcus von Appen (events)`_
   implementation.  I really appreciate his simple approach.


-- _`Marcus von Appen (events)`: https://bitbucket.org/marcusva/python-utils/src/default/utils/events.py

"""

__all__ = ["EventHandler", "MPEventHandler"]

import logging
log = logging.getLogger(__name__)

_HASMP = True
try:
    from multiprocessing import Pool
except ImportError:
    _HASMP = False

GLOBAL_HANDLERS = dict()

def get_event(event_name):
    """Returns a named :py:class:`EventHandler` instance from global."""
    handler = GLOBAL_HANDLERS.get(event_name, None)
    if handler is None:
        handler = MPEventHandler(event_name)
        GLOBAL_HANDLERS[event_name] = handler
    return handler

def on_return_release(event_name):
    """Decorator to add a :py:class:`Event` to functions return.

    The handler funtion will be called with arguments::

        my_return_handler(event_name, ret_val, func, *args, **kwargs)

    By example: to trace a function of your lib, add a decorator with a
    appropriate name.  Mostly the fully qualified python name is a good choice::

        from fontlib.event import on_return_release

        @on_return_release('pkgname.modulename.foobar')
        def foobar(a, b, *args, **kwargs):
            import time
            time.sleep(3)
            return a + b, dict(foo=args, bar=kwargs)

    From outer scope (e.g. in the man loop) you can add a handler wich is called
    on 'pkgname.modulename.foobar' events.  Lets write a handler that dumps
    function arguemt and return value to stout::

        def dump_call(event_name, ret_val, func, *args, **kwargs):
            print("event : " + event_name)
            print("call: "+ func.__name__ + ", "  + str(args) + ", " + str(kwargs))
            print("returned --> " + str(ret_val))
            return 42

    And to register this handler on 'pkgname.modulename.foobar' events::

        event = get_event('pkgname.modulename.foobar')
        event += dump_call

    Now, every time we call foobar the function return is dumped::

        >>> foobar(7,12,"pos-arg1", "arg2", keyword="value")
        event : pkgname.modulename.foobar
        call: foobar, (7, 12, 'pos-arg1', 'arg2'), {'keyword': 'value'}
        returned --> (19, {'foo': ('pos-arg1', 'arg2'), 'bar': {'keyword': 'value'}})
    """
    _ = get_event(event_name)
    def decorator(origin_func):
        def wrapper(*args, **kwargs):
            ret_val = origin_func(*args,**kwargs)
            _(ret_val, origin_func, *args ,**kwargs)
            return ret_val
        return wrapper
    return decorator

class EventHandler:
    """A simple event handling class, which manages callbacks to be executed.

     usage ::

       >>> my_event = EventHandler("my.event.name")
       >>> def foo(event_name, *args, **kwargs):
       ...     print("foo:: %s -->  %s // %s" % (event_name, args, kwargs))
       ...     return 42

       >>> my_event += foo
       >>> my_event('hello', name='world') # call the event prints & return
       foo:: my.event.name -->  ('hello', ) // {'name': 'world'}
       [42]
       >>> my_event -= foo  # now unregister the foo handler
       >>> my_event('hello', name = 'world') # no more handler result in ..
       []

    """
    def __init__(self, event_name):
        self.callbacks = []
        self.event_name = event_name

    def __call__(self, *args, **kwargs):
        """Executes all callbacks.

        Executes all connected callbacks in the order of addition, passing the
        event_name of the EventHandler as first argument and the optional args as
        second, third, ... *keyword arguments* (``**kwargs``) are also passed through.

        """
        return [callback(self.event_name, *args, **kwargs) for callback in self.callbacks]

    def add(self, callback):
        """Adds a callback to the EventHandler."""
        if not callable(callback):
            raise TypeError("callback mus be callable")
        self.callbacks.append(callback)

    def __iadd__(self, callback):
        """Adds a callback to the EventHandler.

        Support ``self += callback`` operator.

        """
        self.add(callback)
        return self

    def remove(self, callback):
        """Removes a callback from the EventHandler."""
        self.callbacks.remove(callback)

    def __isub__(self, callback):
        """Removes a callback from the EventHandler.

        Support ``self -= callback`` operator.
        """
        self.remove(callback)
        return self

    def __len__(self):
        """Gets the amount of callbacks connected to the EventHandler."""
        return len(self.callbacks)

    def __getitem__(self, index):
        return self.callbacks[index]

    def __setitem__(self, index, value):
        self.callbacks[index] = value

    def __delitem__(self, index):
        del self.callbacks[index]




def _mp_callback(args):
    # args = (function, event_name, (args))
    fargs = args[2]
    return args[0](args[1], *fargs)


class MPEventHandler(EventHandler):
    """An asynchronous event handling class in which callbacks are
    executed in parallel.

    It is the responsibility of the caller code to ensure that every
    object used maintains a consistent state. The MPEventHandler class
    will not apply any locks, synchronous state changes or anything else
    to the arguments being used. Consider it a "fire-and-forget" event
    handling strategy
    """
    def __init__(self, event_name, maxprocs=None):
        if not _HASMP:
            raise RuntimeError("MPEventHandler: no multiprocessing support found!")
        super(MPEventHandler, self).__init__(event_name)
        self.maxprocs = maxprocs

    def __call__(self, *args): # FIXME needs **kwargs
        if self.maxprocs is not None:
            pool = Pool(processes=self.maxprocs)
        else:
            pool = Pool()
        psize = len(self.callbacks)
        pv = zip(self.callbacks, [self.event_name] * psize, [args[:]] * psize)
        results = pool.map_async(_mp_callback, pv)
        pool.close()
        pool.join()
        return results

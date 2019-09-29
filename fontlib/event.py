# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""Simple event & handler implementation.

.. hint::

   Most of the class :py:class:`Event` was copied from `Marcus von Appen
   (events)`_ implementation.  I really appreciate his simple approach.


-- _`Marcus von Appen (events)`: https://bitbucket.org/marcusva/python-utils/src/default/utils/events.py

"""

__all__ = ["Event", "AsyncEvent"]

import os
import logging
log = logging.getLogger(__name__)

_HASMP = True
try:
    from multiprocessing import Pool
except ImportError:
    _HASMP = False

GLOBAL_HANDLERS = dict()

def get_event(event_name):
    """Returns a named :py:class:`Event` instance from global."""
    handler = GLOBAL_HANDLERS.get(event_name, None)
    if handler is None:
        handler = Event(event_name)
        GLOBAL_HANDLERS[event_name] = handler
    return handler

# def on_return_release(event_name):
#     """Decorator to add a :py:class:`Event` to functions return.

#     The handler funtion will be called with arguments::

#         my_return_handler(event_name, ret_val, func, *args, **kwargs)

#     By example: to trace a function of your lib, add a decorator with a
#     appropriate name.  Mostly the fully qualified python name is a good choice::

#         from fontlib.event import on_return_release

#         @on_return_release('pkgname.modulename.foobar')
#         def foobar(a, b, *args, **kwargs):
#             import time
#             time.sleep(3)
#             return a + b, dict(foo=args, bar=kwargs)

#     From outer scope (e.g. in the man loop) you can add a handler wich is called
#     on 'pkgname.modulename.foobar' events.  Lets write a handler that dumps
#     function arguemt and return value to stout::

#         def dump_call(event_name, ret_val, func, *args, **kwargs):
#             print("event : " + event_name)
#             print("call: "+ func.__name__ + ", "  + str(args) + ", " + str(kwargs))
#             print("returned --> " + str(ret_val))
#             return 42

#     And to register this handler on 'pkgname.modulename.foobar' events::

#         event = get_event('pkgname.modulename.foobar')
#         event += dump_call

#     Now, every time we call foobar the function return is dumped::

#         >>> foobar(7,12,"pos-arg1", "arg2", keyword="value")
#         event : pkgname.modulename.foobar
#         call: foobar, (7, 12, 'pos-arg1', 'arg2'), {'keyword': 'value'}
#         returned --> (19, {'foo': ('pos-arg1', 'arg2'), 'bar': {'keyword': 'value'}})
#     """
#     _ = get_event(event_name)
#     def decorator(origin_func):
#         def wrapper(*args, **kwargs):
#             ret_val = origin_func(*args,**kwargs)
#             _(ret_val, origin_func, *args ,**kwargs)
#             return ret_val
#         return wrapper
#     return decorator

# def on_call_release(event_name):
#     """Decorator to add a :py:class:`Event` to function calls.

#     The handler function will be called with arguments::

#         my_call_handler(event_name, func, *args, **kwargs)

#     """
#     _ = get_event(event_name)
#     def decorator(origin_func):
#         def wrapper(*args, **kwargs):
#             _(origin_func, *args ,**kwargs)
#             return origin_func(*args,**kwargs)
#         return wrapper
#     return decorator

def add_handler(event_name):
    """Decorator to add a function as event handler."""
    def decorator(origin_func):
        _ = get_event(event_name)
        _ += origin_func
        return origin_func
    return decorator


class Event:
    """A simple event handling class, which manages callbacks to be executed.

     usage ::

       >>> my_event = Event("my.event.name")
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
        """Executes all callbacks synchronous.

        Executes all connected callbacks synchronous in the order of addition,
        passing the :py:class:`Event` object as first argument.  Arguments
        (``*args``) and *keyword arguments* (``**kwargs``) are also passed
        through.

        """
        for handler in self.callbacks:
            handler(*args, **kwargs)

    def add(self, callback):
        """Adds a callback to the Event."""
        if not callable(callback):
            raise TypeError("callback mus be callable")
        self.callbacks.append(callback)

    def __iadd__(self, callback):
        """Adds a callback to the Event.

        Support ``self += callback`` operator.

        """
        self.add(callback)
        return self

    def remove(self, callback):
        """Removes a callback from the Event."""
        self.callbacks.remove(callback)

    def __isub__(self, callback):
        """Removes a callback from the Event.

        Support ``self -= callback`` operator.
        """
        self.remove(callback)
        return self

    def __len__(self):
        """Gets the amount of callbacks connected to the Event."""
        return len(self.callbacks)

    def __getitem__(self, index):
        return self.callbacks[index]

    def __setitem__(self, index, value):
        self.callbacks[index] = value

    def __delitem__(self, index):
        del self.callbacks[index]

class AsyncEvent(Event):
    """Executes all callbacks asynchronous.

    Executes all connected callbacks asynchronous, passing the :py:class:`Event`
    object as first argument.  Arguments (``*args``) and *keyword arguments*
    (``**kwargs``) are also passed through.

    It is the responsibility of the caller code to ensure that every object used
    maintains a consistent state. The MPEvent class will not apply any locks,
    synchronous state changes or anything else to the arguments being
    used. Consider it a "fire-and-forget" event handling strategy

    """
    def __init__(self, event_name, maxprocs=None):
        if not _HASMP:
            raise RuntimeError("MPEvent: no multiprocessing support found!")
        super().__init__(event_name)
        self.maxprocs = maxprocs or os.cpu_count() // 3

    def __call__(self, *args, **kwargs):
        pool = Pool(processes=self.maxprocs)
        for handler in self.callbacks:
            pool.apply_async(handler, args, kwargs)
        pool.close()

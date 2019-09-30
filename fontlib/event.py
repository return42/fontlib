# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""Simple event & handler implementation.

Events are managed by a global event dispatcher.  The global dispatcher manage
events by their names.  Emitters and observers are always use the
:py:func:`get_event` function to get :py:class:`AsyncEvent` instances.

Emitters POV::

    start = 1; end = 42
    for i in range(start, end+1):
        get_event('foo-ticker')(i, start, end)
        ...

Observers POV::

    def my_observer(i, start, end):
        print("foo ticker round: %%s/[%%s]%%s" % (i, start, end))
    get_event('foo-ticker').add(my_observer)


.. hint::

   Most of the class :py:class:`Event` was copied from `Marcus von Appen
   (events)`_ implementation.  I really appreciate his simple approach.


-- _`Marcus von Appen (events)`: https://bitbucket.org/marcusva/python-utils/src/default/utils/events.py

"""

__all__ = ["get_event"]

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
    """Returns a named :py:class:`AsyncEvent` instance from global event dispatcher."""
    handler = GLOBAL_HANDLERS.get(event_name, None)
    if handler is None:
        handler = AsyncEvent(event_name)
        GLOBAL_HANDLERS[event_name] = handler
    return handler

class Event:
    """A simple event handling class, which manages callbacks to be executed.

     usage ::

       >>> my_event = Event("my.event.name")
       >>> def foo(event_name, *args, **kwargs):
       ...     print("foo:: %s -->  %s // %s" % (event_name, args, kwargs))
       ...     return 42

       >>> my_event += foo
       >>> my_event('hello', name='world') # call the event and foo will print ..
       foo:: my.event.name -->  ('hello', ) // {'name': 'world'}
       >>> my_event -= foo  # now unregister the foo handler
       >>> my_event('hello', name = 'world') # no more handlers / no print output
       >>>

    """
    def __init__(self, event_name):
        self.callbacks = []
        self.event_name = event_name

    def __call__(self, *args, **kwargs):
        """Executes all callbacks **synchronous**.

        Executes all connected callbacks synchronous in the order of addition.
        Positional arguments (``*args``) and *keyword arguments* (``**kwargs``)
        are passed through.

        """
        for handler in self.callbacks:
            handler(*args, **kwargs)

    def add(self, callback):
        """Adds a callback to the event."""
        if not callable(callback):
            raise TypeError("callback must be callable")
        self.callbacks.append(callback)

    def __iadd__(self, callback):
        """Adds a callback to the event.

        Support of the ``self += callback`` operator.

        """
        self.add(callback)
        return self

    def remove(self, callback):
        """Removes a callback from the event."""
        self.callbacks.remove(callback)

    def __isub__(self, callback):
        """Removes a callback from the event.

        Support of the ``self -= callback`` operator.

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
    """Executes all callbacks **asynchronous**.

    Executes all connected callbacks asynchronous.  Positional arguments
    (``*args``) and *keyword arguments* (``**kwargs``) are passed through.

    It is the responsibility of the caller code to ensure that every object used
    maintains a consistent state.  The AsyncEvent class will not apply any
    locks, synchronous state changes or anything else to the arguments being
    used.  Consider it a *fire-and-forget* event handling strategy.

    `Picklability
    <https://docs.python.org/3/library/multiprocessing.html#all-start-methods>`__:

        Ensure that the arguments to the methods of proxies are picklable.
        E.g. lambda is not pickable, for more informations read: `What can be
        pickled and unpickled?
        <https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled>`__

    Lambda functions can be replaced by *objects as functions*::

        class EventPrinter:
            def __init__(self, s):
                self.string = s
            def __call__(self):
                print(self.string)

        get_event('my.event').add(
            EventPrinter('hello: the my.event has beend released.'))

    """
    def __init__(self, event_name, maxprocs=None):
        if not _HASMP:
            raise RuntimeError("MPEvent: no multiprocessing support found!")
        super().__init__(event_name)
        self.maxprocs = maxprocs or os.cpu_count() // 3

    def __call__(self, *args, **kwargs):

        # -  https://docs.python.org/library/multiprocessing.html#module-multiprocessing.pool
        #
        #    > Pool objects now support the context management protocol – see
        #    > Context Manager Types. __enter__() returns the pool object, and
        #    > __exit__() calls terminate().
        #
        # .. hint::
        #
        #    To inhibit implicite call of ``pool.terminate()`` we don't use the
        #    *context management protocol* of the multiprocessing.Pool class!!!

        pool = Pool(processes=self.maxprocs)
        for handler in self.callbacks:
            pool.apply_async(handler, args, kwargs)
        pool.close()

# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""Simple *observer pattern* implementation, where subjects are named events.

Events are managed by a global event dispatcher.  The global dispatcher arranges
the events according to their name.  Emitters and observers are always use the
:py:func:`get_event` function to get :py:class:`Event` instances.  Application's
main loop has to init the global dispatcher first (:py:func:`init_dispatcher`).

Emitter's POV::

    start = 1; end = 42
    for i in range(start, end+1):
        event.emit('foo-ticker', i, start, end)
        ...

Observer's POV::

    def my_observer(i, start, end):
        print("foo ticker round: %s/[%s]%s" % (i, start, end))
    event.add('foo-ticker', my_observer)


.. hint::

   Most of the class :py:class:`Event` was copied from `Marcus von Appen
   (events)`_ implementation.  I really appreciate his simple approach.


-- _`Marcus von Appen (events)`: https://bitbucket.org/marcusva/python-utils/src/default/utils/events.py

"""

__all__ = [
    'init_dispatcher'
    , 'get_event'
    , 'emit'
    , 'add'
    , 'remove'
    , 'Event'
    , 'AsyncThreadEvent'
    , 'AsyncProcEvent'
]

import os
import logging
import threading
from multiprocessing import Pool

log = logging.getLogger(__name__)

_DISPATCHER = None
_EVENT_CLASS = None

def init_dispatcher(event_cls=None):
    """Init global dispatcher.

    :param event_cls: Event factory, a :py:class:`Event` (sub-)class. Function
      :py:func:`get_event` will return instances of this class.

      - :py:class:`Event` (synchronous)
      - :py:class:`AsyncProcEvent`
      - :py:class:`AsyncThreadEvent`

    """
    global _DISPATCHER, _EVENT_CLASS # pylint: disable=global-statement
    if _DISPATCHER is not None or _EVENT_CLASS is not None:
        raise RuntimeError('re-init of global dispatcher is not supported')

    if event_cls is None:
        event_cls = AsyncThreadEvent
    _EVENT_CLASS = event_cls
    _DISPATCHER = dict()

def get_event(event_name):
    """Returns a named :py:class:`Event` instance from global event dispatcher.

    The returned object is an instance from the global dispatcher.  The event
    type is set in :py:func:`init_dispatcher`

    :return: event instance from global dispatcher
    :rtype:
      - :py:class:`Event` (synchronous)
      - :py:class:`AsyncProcEvent`
      - :py:class:`AsyncThreadEvent`

    """
    global _DISPATCHER, _EVENT_CLASS  # pylint: disable=global-statement
    if _DISPATCHER is None:
        raise RuntimeError('init of global dispatcher is needed first!')
    handler = _DISPATCHER.get(event_name, None)
    if handler is None:
        handler = _EVENT_CLASS(event_name)
        _DISPATCHER[event_name] = handler
    return handler

def emit(name, *args, **kwargs):
    """Emit event and pass through arguments to the observers.

    :param str name:  name of the event

    The event is taken from the global dispatcher (see :py:func:`get_event`)

    """
    event = get_event(name)
    event(*args, **kwargs)


def add(name, callback):
    """Add observer (<callback>) to event.

    :param str name:  name of the event
    :param func:  callback function

    The event is taken from the global dispatcher (see :py:func:`get_event`)

    """
    event = get_event(name)
    event += callback

def remove(name, callback):
    """Remove observer (<callback>) from event.

    :param str name:  name of the event
    :param callback:  callback function to remove

    The event is taken from the global dispatcher (see :py:func:`get_event`)

    """
    event = get_event(name)
    event -= callback


class Event:

    """A simple event handling class, which manages callbacks to be executed.

     usage ::

       >>> my_event = Event("my.event.name")
       >>> def foo(*args, **kwargs):
       ...     print("foo:: %s // %s" % (args, kwargs))
       ...     return 42

       >>> my_event += foo
       >>> my_event('hello', name='world') # call the event and foo will print ..
       foo:: ('hello', ) // {'name': 'world'}
       >>> my_event -= foo  # now unregister the foo handler
       >>> my_event('hello', name = 'world') # no more handlers / no print output
       >>>

    """
    def __init__(self, event_name):
        self.callbacks = []
        self.event_name = event_name

    def emit_sync(self, *args, **kwargs):
        """Executes all callbacks **synchronous**.

        Executes all connected callbacks synchronous in the order of addition.
        Positional arguments (``*args``) and *keyword arguments* (``**kwargs``)
        are passed through.

        """
        log.debug('emit synchronous: %s', self.event_name)
        for handler in self.callbacks:
            handler(*args, **kwargs)

    __call__ = emit_sync

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

class AsyncThreadEvent(Event):
    """Executes all callbacks in **asynchronous** threads.

    Executes all connected callbacks asynchronous.  Positional arguments
    (``*args``) and *keyword arguments* (``**kwargs``) are passed through.

    It is the responsibility of the caller code to ensure that every object used
    maintains a consistent state.  The AsyncThreadEvent class will not apply any
    locks, synchronous state changes or anything else to the arguments being
    used.  Consider it a *fire-and-forget* event handling strategy.

    """

    def emit_async(self, *args, **kwargs):
        """Executes all callbacks in a **asynchronous** threads."""

        for handler in self.callbacks:
            thread = threading.Thread(
                name = self.event_name
                , daemon = True
                , target = handler, args = args, kwargs = kwargs
            )
            thread.start()

    __call__ = emit_async

class AsyncProcEvent(Event):
    """Executes all callbacks in a **asynchronous** process pool.

    Executes all connected callbacks asynchronous.  Positional arguments
    (``*args``) and *keyword arguments* (``**kwargs``) are passed through.

    It is the responsibility of the caller code to ensure that every object used
    maintains a consistent state.  The AsyncProcEvent class will not apply any
    locks, synchronous state changes or anything else to the arguments being
    used.  Consider it a *fire-and-forget* event handling strategy.

    `Picklability
    <https://docs.python.org/3/library/multiprocessing.html#all-start-methods>`__:

        Ensure that the arguments to the methods of proxies are picklable.
        E.g. lambda is not pickable, for more informations read: `What can be
        pickled and unpickled?
        <https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled>`__

    Lambda functions can be replaced by *objects as functions*::

        class EventMsg(str):
            def __call__(self, *args, **kwargs):
                print(self)

        get_event('my.event').add(
            EventMsg('hello: the my.event has beend released.'))

    """
    def __init__(self, event_name, maxprocs=None):
        super().__init__(event_name)
        self.maxprocs = maxprocs or os.cpu_count() // 3

    def emit_async(self, *args, **kwargs):
        """Executes all callbacks in a **asynchronous** process pool."""

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

    __call__ = emit_async

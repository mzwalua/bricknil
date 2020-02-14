# Copyright 2019 Virantha N. Ekanayake
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Super-class of all the Tasks in the event-loop
"""
from enum import Enum
from itertools import chain
from asyncio import iscoroutinefunction
import logging
from blinker import signal
from blinker.base import Signal

async def __emit(signal, sender, *args, **kwargs):
    """
    Emit (send) given signal, passing args and kwargs to handler.
    This is much like blinker's .send(), except that:

      * it is an asynchronous method so it can be used within asyncio / curio
        event queues
      * allow receivers (handlers) to be either normal functions or coroutines
      * allow passing positional arguments (this is handy as it does not require
        emitter to know receivers's signature)
      * does not return anything

    >>> s = signal("foo")
    >>> s.connect(lambda sender, arg : print(arg))
    >>> s.emit(self, 42)
    42
    """
    receivers = list(signal.receivers_for(sender)) if signal.receivers else []
    for receiver in filter(lambda e : not iscoroutinefunction(e), receivers):
        receiver(sender, *args, **kwargs)
    for receiver in filter(lambda e : iscoroutinefunction(e), receivers):
        await receiver(sender, *args, **kwargs)

Signal.emit = __emit

class Process:
    """Subclass this for anything going into the Async Event Loop and can signal
       events such as hubs and peripherals.

       This class keeps track of a unique numeric ID for each process and its name
       (for debugging purposes).

       Each process also defines a list of (named) signals. Clients may connect
       (subscribe) and react. For example, one may connect to peripeheral "notify"
       (or "notify::<mode>") signal to get informed of new sensor reading.

       It also provides some utilty functions to log messages at various levels.

       Attributes:
          id (int) : Process ID (unique)
          name (str):  Human readable name for process (does not need to be unique)

    """

    _next_id = 0

    _signals_ = []

    def __init__(self, name):
        self.name = name

        # Assign ID
        self.id = Process._next_id
        Process._next_id += 1

        self.logger = logging.getLogger(str(self))

    def __str__(self):
        return f'{self.name}.{self.id}'

    def __repr__(self):
        return f'{type(self).__name__}("{self.name}")'

    def signals(self):
        """
        Return list of all signals (as strings) supported by this object
        """
        mine = self._signals_ if hasattr(self, '_signals_') else []
        inherited = super().signals() if hasattr(super(), 'signals') else []
        return chain(mine, inherited)

    def connect(self, name, callable):
        """
        Connect callable to signal with given name, i.e., arrange so that
        callable is called each time signal is emitted. Callable is held on
        strongly.
        """
        assert name in self.signals(), "signal %s not supported by %s" % (name, self)
        signal(name).connect(callable, sender=self, weak=False)

    async def emit(self, name, *args, **kwargs):
        """
        Emit given signal, i.e., call all handlers connected to it, passing
        *args and **kwargs to the handler
        """
        assert name in self.signals(), "signal %s not supported by %s" % (name, self)
        await signal(name).emit(self, *args, **kwargs)

    def message(self, m : str , level = logging.INFO):
        """Print message *m* if its level is lower than the instance level"""

        if level == logging.DEBUG:
            self.logger.debug(m)
        elif level == logging.INFO:
            self.logger.info(m)
        elif level == logging.ERROR:
            self.logger.error(m)

    def message_info(self, m):
        """Helper function for logging messages at INFO level"""
        self.message(m, logging.INFO)

    def message_debug(self, m):
        """Helper function for logging messages at DEBUG level"""
        self.message(m, logging.DEBUG)

    def message_error(self, m):
        """Helper function for logging messages at ERROR level"""
        self.message(m, logging.ERROR)

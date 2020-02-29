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

"""Utility functions to attach sensors/motors and start the whole event loop

    #. The decorator :class:`attach` to specify peripherals that
       connect to a hub (which enables sensing and motor control functions),
    #. The function :func:`start` that starts running the BLE communication queue, and all the hubs, in the event-loop system

"""

import logging
import pprint
from asyncio import run, sleep, Queue, get_event_loop, all_tasks
from asyncio import create_task as spawn
from functools import partial, wraps
import uuid

# Local imports
from .process import Process
from .ble_queue import BLEventQ
from .hub import PoweredUpHub, BoostHub, Hub

import threading

# Actual decorator that sets up the peripheral classes
# noinspection PyPep8Naming
class attach:
    """ Class-decorator to attach peripherals onto a Hub

        Injects sub-classes of `Peripheral` as instance variables on a Hub
        such as the PoweredUp Hub, akin to "attaching" a physical sensor or
        motor onto the Hub.

        Before you attach a peripheral with sensing capabilities,
        you need to ensure your `Peripheral` sub-class has the matching
        call-back method 'peripheralname_change'.

        Examples::

            @attach(PeripheralType,
                    name="instance name",
                    port='port',
                    capabilities=[])

        Warnings:
            - No support for checking to make sure user put in correct parameters
            - Identifies capabilities that need a callback update handler based purely on
              checking if the capability name starts with the string "sense*"

    """
    def __init__(self, peripheral_type, **kwargs):
        # TODO: check here to make sure parameters were entered
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            print(f'decorating with {peripheral_type}')
        self.peripheral_type = peripheral_type
        self.kwargs = kwargs

    def __call__ (self, cls):
        """
            Since the actual Hub sub-class being decorated can have __init__ params,
            we need to have a wrapper function inside here to capture the arguments
            going into that __init__ call.

            Inside that wrapper, we do the following:

            # Instance the peripheral that was decorated with the saved **kwargs
            # Check that any `sense_*` capabiilities in the peripheral have an
              appropriate handler method in the hub class being decorated.
            # Instance the Hub
            # Set the peripheral instance as an instance variable on the hub via the
              `Hub.attach_sensor` method

        """
        # Define a wrapper function to capture the actual instantiation and __init__ params
        @wraps(cls)
        def wrapper_f(*args, **kwargs):
            #print(f'type of cls is {type(cls)}')
            peripheral = self.peripheral_type(**self.kwargs)
            o = cls(*args, **kwargs)
            o.message_debug(f"Decorating class {cls.__name__} with {self.peripheral_type.__name__}")
            o.attach_sensor(peripheral)
            return o
        return wrapper_f

async def main(system):
    """
    Entry-point coroutine that handles everything. This is to be run run
    in bricknil's main loop.

    You normally don't need to use this directly, instead use start()
    """
    try:
        # Instantiate the Bluetooth LE handler/queue
        ble_q = BLEventQ.instance

        # Call the user's system routine to instantiate the processes
        await system()

        hub_tasks = []

        # Connect all the hubs first before enabling any of them
        for hub in Hub.hubs:
            await hub.connect()

        # Start each hub
        for hub in Hub.hubs:
            task_run = spawn(hub.run())
            hub_tasks.append(task_run)

        # Now wait for the tasks to finish
        ble_q.message_info(f'Waiting for hubs to end')

        for task in hub_tasks:
            await task
        ble_q.message_info(f'Hubs end')
    finally:
        for hub in Hub.hubs:
            await hub.disconnect()

        # Print out the port information in debug mode
        for hub in Hub.hubs:
            if hub.query_port_info:
                hub.message_info(pprint.pformat(hub.port_info))

        # At this point no device should be connected, but
        # just to make sure...
        await ble_q.disconnect_all()

# Reference to the loop running
__loop = None

def start(user_system_setup_func, loop=None): #pragma: no cover
    """
        Main entry point into running everything.

        Just pass in the async co-routine that instantiates all your hubs, and this
        function will take care of the rest.  This includes:

        - Initializing the bluetooth interface object
        - Starting up the user async co-routines inside the asyncio event loop
    """
    global __loop
    __loop = get_event_loop()
    __loop.run_until_complete(main(user_system_setup_func))

def stop():
    global __loop
    if __loop != None:
        tasks = all_tasks(__loop)
        for task in tasks:
            task.cancel()




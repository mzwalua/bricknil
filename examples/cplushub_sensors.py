#!/usr/bin/env python3

import logging
from asyncio import sleep
from bricknil import attach, start
from bricknil.hub import CPlusHub
from bricknil.sensor import Button
from bricknil.sensor import LED
from bricknil.const import Color
from bricknil.sensor import VoltageSensor
from bricknil.sensor import CurrentSensor
from bricknil.sensor.sensor import PoweredUpHubIMUAccelerometer
from bricknil.sensor.sensor import PoweredUpHubIMUGyro
from bricknil.sensor.sensor import PoweredUpHubIMUPosition

@attach(Button, name='hub_btn', capabilities=['sense_press'])
@attach(LED, name='hub_led')
#@attach(VoltageSensor, name='voltage', capabilities=['sense_l'])
#@attach(CurrentSensor, name='current', capabilities=['sense_l'])
#@attach(PoweredUpHubIMUPosition, name='IMUPos', capabilities=['sense_pos'])
class truck(CPlusHub):

    async def hub_btn_change(self):
        print('hub_btn')

#    async def voltage_change(self):
#       print('voltage: ',self.voltage.sense_l);
#       pass

#    async def current_change(self):
#       print('current: ',self.current.sense_l);
#       pass

#    async def IMUPos_change(self):
#       print('IMUPos: ',self.IMUPos.sense_pos);
#       pass

    async def run(self):
        print('Running')
        print('ID: ',self.ble_id);

        await self.hub_led.set_color(Color.green)
        await sleep(10)

async def system():
    hub = truck('truck', True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    start(system)

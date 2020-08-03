#!/usr/bin/env python3

import logging
from asyncio import sleep
from bricknil import attach, start
from bricknil.hub import CPlusHub
from bricknil.const import Color
from bricknil.sensor import LED
from bricknil.sensor import VoltageSensor
from bricknil.sensor import CurrentSensor
from bricknil.sensor import PoweredUpHubIMUTemperature
from bricknil.sensor import PoweredUpHubIMUAccelerometer
from bricknil.sensor import PoweredUpHubIMUGyro
from bricknil.sensor import PoweredUpHubIMUPosition
from bricknil.sensor import Button

@attach(Button, name='hub_btn', capabilities=['sense_press'])
@attach(LED, name='hub_led')
#@attach(VoltageSensor, name='voltage', capabilities=['sense_l'])
#@attach(CurrentSensor, name='current', capabilities=['sense_l'])
@attach(PoweredUpHubTemperature, name='temp1', port=60, capabilities=['sense_temp'])
@attach(PoweredUpHubTemperature, name='temp2', port=96, capabilities=['sense_temp'])
#@attach(PoweredUpHubIMUPosition, name='IMUPos', capabilities=['sense_pos'])
class truck(CPlusHub):

    stop=0

    async def hub_btn_change(self):
        print('hub_btn')
        self.stop = 1

#    async def voltage_change(self):
#       print('voltage: ',self.voltage.sense_l);
#       pass

#    async def current_change(self):
#       print('current: ',self.current.sense_l);
#       pass

    async def temp1_change(self):
        print('temp1: ',self.temp1.sense_temp);
        pass

    async def temp2_change(self):
        print('temp2: ',self.temp2.sense_temp);
        pass

#    async def IMUPos_change(self):
#       print('IMUPos: ',self.IMUPos.sense_pos);
#       pass

    async def run(self):
        print('Running')
        print('ID: ',self.ble_id);

        await self.hub_led.set_color(Color.green)

        await sleep(1)

        self.stop=0
        while 1:
            await sleep(0.001)

            if self.stop==1:
                break


async def system():
    hub = truck('truck', True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    start(system)

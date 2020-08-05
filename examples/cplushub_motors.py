#!/usr/bin/env python3

import logging
from asyncio import sleep
from bricknil import attach, start
from bricknil.hub import CPlusHub
from bricknil.const import Color
from bricknil.sensor import LED
from bricknil.sensor import Button
from bricknil.sensor.motor import CPlusXLMotor
from bricknil.sensor.motor import CPlusLargeAngularPositionMotor

@attach(Button, name='hub_btn', capabilities=['sense_press'])
@attach(LED, name='hub_led')
@attach(CPlusXLMotor, name='drive', port=0, capabilities=['sense_pos'])
@attach(CPlusLargeAngularPositionMotor, name='mot', port=3, capabilities=['sense_pos'])
class truck(CPlusHub):

    stop=0

    async def hub_btn_change(self):
        print('hub_btn')
        self.stop = 1

    async def mot_change(self):
        print('mot: ',self.mot.sense_pos)
        pass

    async def drive_change(self):
        print('drive: ',self.drive.sense_pos)
        pass

    async def run(self):
        print('Running')
        print('ID: ',self.ble_id);

        await self.hub_led.set_color(Color.green)

        await sleep(2)

#        await self.mot.set_pos(-45, speed=100)
        await self.drive.set_speed(20)
        await sleep(2)

        self.stop=0
        while 1:
            await sleep(0.001)

            if self.stop==1:
#                await self.mot.set_pos(0, speed=100)
                await self.drive.set_pos(0, speed=100)
                await sleep(1)
                break


async def system():
    hub = truck('truck', True)

if __name__ == '__main__':
#    logging.basicConfig(level=logging.DEBUG)
    start(system)

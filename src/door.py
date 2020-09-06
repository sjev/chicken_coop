import uasyncio as asyncio
import json
from machine import Pin
import time

class Timer:
    """ simple timekeeper class, in ms"""
    def __init__(self,t=None):
        self.start = time.ticks_ms()
        self._timeout = t

    def elapsed(self):
        return time.ticks_ms()-self.start

    @property
    def timeout(self):
        if self._timeout is None:
            return False
        else:
            return self.elapsed() > self._timeout

    def reset(self):
        self.start = time.ticks_ms()

class Door:

    outputs = [('d1',5),('d2',4)]
    inputs = [('d0',16),('d5',14)]
    timeout = 5000

    def __init__(self):
        self.pins = {}
        self.target_state = None
        self.busy = False

        for name,gpio in self.outputs:
            self.pins[name] = Pin(gpio, Pin.OUT)
        for name,gpio in self.inputs:
            self.pins[name] = Pin(gpio, Pin.IN)

    def off(self,pinName):
        self.pins[pinName].value(0)

    def on(self,pinName):
        self.pins[pinName].value(1)

    def toggle(self,pinName):
        self.pins[pinName].value(1-self.pins[pinName].value())

    def motorUp(self):
        self.on('d1')
        self.off('d2')

    def motorDown(self):
        self.on('d2')
        self.off('d1')

    def motorOff(self):
        self.off('d1')
        self.off('d2')

    def switch_states(self):
        return {'s0':self.pins['d0'].value(),'s1':self.pins['d5'].value()}

    async def open(self):

        if self.busy:
            print('door is busy')
            return

        self.busy = True
        self.target_state = 1
        if self.state == 'closed' or (self.state == 'undefined'):
            print('Opening door')
            tim = Timer(self.timeout)
            self.motorUp()
            while (not tim.timeout) and (not self.state == "open"):
                await asyncio.sleep_ms(200)

            self.motorOff()
            print('Timer elapsed:' , tim.elapsed())
        self.busy = False

    async def close(self):

        if self.busy:
            print('door is busy')
            return

        self.busy = True
        self.target_state = 0
        if (self.state == 'open') or (self.state == 'undefined'):
            print('Closing door')
            tim = Timer(self.timeout)
            self.motorDown()
            while (not tim.timeout) and (not self.state == "closed"):
                await asyncio.sleep_ms(200)

            self.motorOff()
            print('Timer elapsed:' , tim.elapsed())
        self.busy = False

    @property
    def state(self):
        """ get door state
        d0 - upper switch
        d1 - lower switch

        closed: both 0
        open: d1=1, d0=1


        """
        top = self.pins['d0'].value()
        bottom = self.pins['d5'].value()

        if top==1 and bottom==1:
            return 'open'
        elif top==0 and bottom==0:
            return 'closed'
        else:
            return 'undefined'

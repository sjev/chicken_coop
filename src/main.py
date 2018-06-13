from machine import Pin
import time


class Board:
    
    # name - gpio pairs
    outputs = [('led',2),('d1',5),('d2',4)]
    
    def __init__(self):

        self.pins = {}
        for name,gpio in self.outputs:
            self.pins[name] = Pin(gpio, Pin.OUT)
       
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


print('Running main.py')



board = Board()

while True:
    board.toggle('led')
    time.sleep(1)


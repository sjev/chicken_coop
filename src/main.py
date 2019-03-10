from machine import Pin
import time
import config
from umqtt.simple import MQTTClient
import ntptime

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

def mqttCallback(topic,msg):
    print('Topic: %s Message:%s' % (topic,msg))

    global client

    if topic == b'coop/door/cmd': # received command
        client.publish(b'coop/door/action',msg) # echo command
        
        
def printInfo():
    """ print diagnostic info to serial """
    from network import WLAN
    wifi = WLAN()
    
      
    
    print('ifconfig :', wifi.ifconfig())
    print('rssi: ',wifi.status('rssi'))

def mainLoop(client,board):
    
    counter = 0
    client.publish('coop/status','online')

    while True:
        board.toggle('led')
        counter +=  1
        
        client.check_msg()
        
        time.sleep(1)
        printInfo()

if __name__ == '__main__':
    print('Running main.py')
    
    
    # set board time
    ntptime.settime()

    board = Board()
    
    client = MQTTClient('chickenMaster', config.broker)
    client.set_callback(mqttCallback)
    
    client.connect()
    
    client.subscribe('coop/door/cmd')

    try:
        mainLoop(client,board)
    finally:
        client.disconnect()
        
    

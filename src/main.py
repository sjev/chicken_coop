from machine import Pin
import time
import config
from mqtt import MQTTClient
import ntptime

KEEP_ALVIVE = 20 # ping every such seconds

class Board:

    # name - gpio pairs
    outputs = [('led',2),('d1',5),('d2',4)]
    inputs = [('d0',16),('d5',14)]

    def __init__(self):

        self.pins = {}
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

    @property
    def doorState(self):
        """ get door state
        d0 - upper switch
        d1 - lower switch

        """
        top = self.pins['d0'].value()
        bottom = self.pins['d5'].value()

        if top==1 and bottom==0:
            return 'open'
        elif top==0 and bottom==1:
            return 'closed'
        else:
            return 'undefined'




def mqttCallback(topic,msg):
    print('Topic: %s Message:%s' % (topic,msg))

    global client, board

    if topic == b'cmnd/coop/DOOR': # received command
        client.publish(b'stat/coop/DOOR',msg) # echo command
        if msg == b'ON':
            board.motorUp()
        elif msg == b'OFF':
            board.motorOff()



def printInfo():
    """ print diagnostic info to serial """
    from network import WLAN
    wifi = WLAN()

    print('ifconfig :', wifi.ifconfig())
    print('rssi: ',wifi.status('rssi'))

def mainLoop(client,board):

    counter = 0


    while True:
        board.toggle('led')


        try:
            client.check_msg()
        except Exception as e:
            print('chck_msg error: %r' % e)

        time.sleep(1)

        if counter % KEEP_ALVIVE == 0:
            client.ping()

        counter += 1
        print(counter,' s0:',board.pins['d0'].value(), ' s1:',board.pins['d5'].value())
        print(board.doorState)
        #printInfo()

if __name__ == '__main__':
    print('Running main.py')


    # set board time
    ntptime.settime()

    board = Board()

    client = MQTTClient('chickenMaster', config.broker,keepalive=KEEP_ALVIVE+5)
    client.DEBUG = True
    client.set_callback(mqttCallback)
    client.set_last_will('tele/coop/LWT','Offline')
    client.connect()
    client.publish('tele/coop/LWT', 'Online')
    client.subscribe('cmnd/coop/DOOR')

    try:
        mainLoop(client,board)
    finally:
        client.disconnect()

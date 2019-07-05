from machine import Pin
import time
import config
from umqtt.simple import MQTTClient
import ntptime
import machine

KEEP_ALVIVE = 20 # ping every such seconds
DOOR_TIMEOUT = 10

topics = {'doorCmd':b'coop/door/switch/cmd',
          'doorSwitchState':b'coop/door/switch/state',
          'tele':b'coop/lwt',
          'doorSensor':b'coop/door/sensor/state'}

class Timer:
    """ simple timekeeper class"""
    def __init__(self,t=None):
        self.start = time.time()
        self._timeout = t

    def elapsed(self):
        return time.time()-self.start

    @property
    def timeout(self):
        if self._timeout is None:
            return False
        else:
            return self.elapsed() > self._timeout

    def reset(self):
        self.start = time.time()

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

    def openDoor(self):

        if self.doorState == 'closed':
            print('Opening door')
            tim = Timer(DOOR_TIMEOUT)
            self.motorUp()
            while (not tim.timeout) and (not self.doorState == "open"):
                time.sleep(0.2)

            self.motorOff()

    def closeDoor(self):

        if self.doorState == 'open':
            print('Closing door')
            tim = Timer(DOOR_TIMEOUT)
            self.motorDown()
            while (not tim.timeout) and (not self.doorState == "closed"):
                time.sleep(0.2)

            self.motorOff()



def mqttCallback(topic,msg):
    print('Topic: %s Message:%s' % (topic,msg))

    if topic == topics['doorCmd']: # received command
        client.publish(topics['doorSwitchState'],msg) # echo command
        if msg == b'ON':
            board.openDoor()
        elif msg == b'OFF':
            board.closeDoor()



def printInfo():
    """ print diagnostic info to serial """
    from network import WLAN
    wifi = WLAN()

    print('ifconfig :', wifi.ifconfig())
    print('rssi: ',wifi.status('rssi'))

def mainLoop(client,board):


    counter = 0
    oldState = board.doorState
    board.on('led')

    while True:
        #board.toggle('led')

        try:
            client.check_msg()
        except Exception as e:
            print('chck_msg error: %r' % e)

        time.sleep(1)

        if counter % KEEP_ALVIVE == 0:
            #client.ping()
            client.publish(topics['tele'], 'Online',retain=False)
        
        counter += 1
        print(counter,' s0:',board.pins['d0'].value(), ' s1:',board.pins['d5'].value())
        print(board.doorState)

        newState = board.doorState
        if oldState != newState:
            print('publishing state')
            client.publish(topics['doorSensor'],newState)
            oldState = newState
        #printInfo()

if __name__ == '__main__':
    print('Running main.py')

    # set board time
    ntptime.settime()

    global client, board
    board = Board()

    board.off('led') # low = led on
    client = MQTTClient('chickenMaster', config.broker,keepalive=KEEP_ALVIVE+5)
    client.DEBUG = True
    client.set_callback(mqttCallback)
    client.set_last_will(topics['tele'],'Offline',retain=True)

    try:
        client.connect()
    except:
        print('Could not connect MQTT. restarting')
        time.sleep(5)
        machine.reset()

    #client.publish(topics['tele'], 'Online',retain=True)
    client.subscribe(topics['doorCmd'])

    try:
        mainLoop(client,board)
    except KeyboardInterrupt:
        print('Keyboard interrupt')
    except:
        machine.reset()

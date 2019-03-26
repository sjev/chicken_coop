import utime
import machine
from umqtt import simple


class MQTTClient(simple.MQTTClient):
    DELAY = 2
    DEBUG = False

    def delay(self):
        utime.sleep(self.DELAY)

    def log(self, s):
        if self.DEBUG:
            print(s)

    def reconnect(self, retries=5):
        i = 0
        while i < retries:
            try:
                return super().connect(False)
            except OSError as e:
                self.log('OS error, reconnecting')
                i += 1
                self.delay()

        # ok, failed
        print('Could not reconnect. Rebooting.')
        machine.reset()

    def publish(self, topic, msg, retain=False, qos=0):
        while 1:
            try:
                self.log('PUB topic:%s msg:%s retain:%s' %(topic,msg,retain))
                return super().publish(topic, msg, retain, qos)
            except OSError as e:
                self.log('OS error')
            self.reconnect()

    def wait_msg(self):
        while 1:
            try:
                return super().wait_msg()
            except OSError as e:
                self.log('OS error')
            self.reconnect()

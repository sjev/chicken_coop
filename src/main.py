import uasyncio as asyncio
from web import WebApp, jsonify
from machine import Pin
import time
import gc
from door import Door
from network import WLAN
from dht_sensor import Sensor

wifi = WLAN()

ENABLE_WDT = False

#watchdog
if ENABLE_WDT:
    from machine import WDT
    wdt = WDT()
    wdt.feed()

door = Door()
sensor = Sensor(13)

webapp = WebApp()
t_start = time.time()


class Led:
    def __init__(self,pin=2):
        self.pin = Pin(pin,Pin.OUT)
    def on(self):
        self.pin.value(0)
    def off(self):
        self.pin.value(1)
    def toggle(self):
        self.pin.value(1-self.pin.value())

async def heartbeat():

    led = Led()
    while True:
        if ENABLE_WDT: wdt.feed()
        led.toggle()
        await asyncio.sleep(1)

async def set_time():
    """
    Set the time from NTP
    """
    while True:
        if wifi.isconnected():
            try:
                from ntptime import settime
                settime()
            except Exception:
                # Ignore errors
                pass
        gc.collect()
        await asyncio.sleep(3600)

async def measure_dht():

    while True:
        sensor.measure()
        await asyncio.sleep(10)

#----------------------------------------------------
@webapp.route('/target_state', method='GET')
def index(request, response):
    yield from jsonify(response, {'target_state':door.target_state})

@webapp.route('/open',method='GET')
def open_cmd(request,response):
    print('open request')
    asyncio.ensure_future(door.open())
    yield from jsonify(response, {'action':'opening'})

@webapp.route('/close',method='GET')
def open_cmd(request,response):
    print('close request')
    asyncio.ensure_future(door.close())
    yield from jsonify(response, {'action':'closing'})

@webapp.route('/cmd', method='POST')
def cmd(request,response):
    yield from request.read_form_data()
    print(request.form)
    try:
        action = request.form['action']
        if action == 'open':
            asyncio.ensure_future(door.open())
        elif action == 'close':
            asyncio.ensure_future(door.close())
    except KeyError:
        pass

    yield from jsonify(response, {'action':action})

@webapp.route('/status',method='GET')
def status(request,response):
    try:
        data = {'uptime':time.time()-t_start, 'door_state': door.state,'rssi':wifi.status('rssi')}
        data['switches'] = door.switch_states()
        data['sensor'] = sensor.data
        data['time'] = time.mktime(time.localtime())
        yield from jsonify(response, data)
    except Exception as e:
        print('error: %r' % e)
        data = {'error':'%r' % e}
        yield from jsonify(response, data)

@webapp.route('/test', method='GET')
def test_fcn(request,response):

    async def count():
        for i in range(10):
            print(i)
            await asyncio.sleep(1)

    asyncio.ensure_future(count())

    yield from jsonify(response, {'data':'test function'})

def main():
    loop = asyncio.get_event_loop()
    loop.create_task(heartbeat())
    #loop.create_task(calc_sunrise_sunset())
    loop.create_task(measure_dht())
    loop.create_task(asyncio.start_server(webapp.handle, '0.0.0.0', 80))
    gc.collect()
    loop.run_forever()


if __name__ == "__main__":
    main()

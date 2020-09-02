# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None) # turn off vendor O/S debugging messages
import config
import machine
import network
import time
import gc


from sys import modules
def reload(mod):
  mod_name = mod.__name__
  del sys.modules[mod_name]
  gc.collect()
  return __import__(mod_name)

def connectWifi():
    """ connect to a wifi network """
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False) # disable access point

    wifi = network.WLAN(network.STA_IF)

    if not wifi.isconnected():

        print('connecting to ',config.ssid)

        #wifi.ifconfig(config.netconfig)
        wifi.active(True)
        wifi.connect(config.ssid, config.wifiPass)
        for retry in range(5):
            if wifi.isconnected():
                break
            else:
                print('Retrying #',retry)
                time.sleep(3)
        if not wifi.isconnected(): # could not connect
            print('Could not connect, rebooting')
            time.sleep(2)
            machine.reset()

    if wifi.isconnected(): # should be connected now
        print('network config:', wifi.ifconfig())

    else: # warn with led and reboot
        print('Connection failed!')
        time.sleep(5)
        print('Restarting')
        machine.reset()


connectWifi()
gc.collect()


# start webrepl
#import webrepl
#webrepl.start()

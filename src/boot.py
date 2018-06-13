# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None) # turn off vendor O/S debugging messages
import config
import machine
import network
import time
import gc


def connectWifi(networks=config.networks):
    """ connect to a wifi network """
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False) # disable access point
    
    sta_if = network.WLAN(network.STA_IF)
    
    if not sta_if.isconnected():
        for essid,password in networks:
            print('connecting to ',essid)
            sta_if.active(True)
            sta_if.connect(essid, password)
            for retry in range(5):
                if sta_if.isconnected():
                    break
                else:
                    print('Retrying #',retry)
                    time.sleep(3)
            if sta_if.isconnected():
                    break
    
    if sta_if.isconnected(): # should be connected now
        print('network config:', sta_if.ifconfig())
    else: # warn with led and reboot
        print('Connection failed!')
        time.sleep(5)
        print('Restarting')
        machine.reset()
        

connectWifi(networks = config.networks)
gc.collect()
# start webrepl
import webrepl
webrepl.start()

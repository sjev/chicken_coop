# configuration


# wifi networks configuration

networks = [('ssid1','pass1'),('ssid2','pass2')]
webreplPass = 'pass3'


# init webrepl
import os
files = os.listdir()
if 'webrepl_cfg.py' not in files:
    with open('webrepl_cfg.py','w') as f:
        f.write("PASS = '%s'" % webreplPass)
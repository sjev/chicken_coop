#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install all files to the board

@author: jev
"""

from  subprocess import check_output


ampy = '/home/jev/anaconda3/bin/ampy'


def runCmd(cmd, port = '/dev/ttyUSB0'):
    """ run ampy command """
    s = ampy+ ' -p '+port+' '+cmd
    print('Running ', s)
    out = check_output(s,shell=True)
    return out

def listFiles():
    out = runCmd('ls')
    files = []
    for line in out.decode().split('\n'):
        if line:
            files.append(line)
    return files

def upload(files):
    for f in files:
        runCmd('put '+f)

def deleteFiles(files):
    
    for f in files:
        runCmd('rm '+f)
 
if __name__ == '__main__':
    
    # delete files 
    l = listFiles()
    print('deleting files: ',l)
    deleteFiles(l)
    
    # upload files
    from pathlib import Path
    path = Path('src')
    files = [str(f) for f in  path.glob('*.py')]
    upload(files)
    
    # add libraries
    print('Please manually copy umqtt. Or use upip if it works')
    
    

#!/usr/bin/env python3

import os
from datetime import datetime

bejeweled_activity = 'com.ea.gp.bej3/.Main'

def start_bejeweled():
    command = 'adb shell am start -n {}'.format(bejeweled_activity)
    os.system(command)

def screenshot(intermediate_name='bejeweled'):
    now = datetime.now()
    filename = '{}-{}.png'.format(intermediate_name, \
            now.strftime("%Y-%m-%d-%H-%M-%S"))
    commands = [
        'adb shell screencap -p /sdcard/{}'.format(filename),
        'adb pull /sdcard/{} .'.format(filename),
    ]
    for command in commands:
        os.system(command)
    return filename

def tap(point):
    command = 'adb shell input tap {0[0]:d} {0[1]:d}'.format(point.xy)
    os.system(command)

def swipe(start_point, end_point, time=100):
    command = 'adb shell input swipe {0[0]:d} {0[1]:d} {1[0]:d} {1[1]:d}'.format(start_point.xy, end_point.xy)
    os.system(command)

if __name__ == '__main__':
    screenshot()

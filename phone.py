#!/usr/bin/env python3

import os
from datetime import datetime

board_resolution = (1080, 1080)
board_offset = (0, 407)
board_size = (8, 8)
jewel_resolution = tuple(round(s / c) 
        for (s, c) in zip(board_resolution, board_size))

def tap_pixel(xy):
    return tuple(
            board_offset[i] + round((xy[i] + 0.5) * jewel_resolution[i])
            for i in range(2))

bejeweled_activity = 'com.ea.gp.bej3/.Main'

def start_bejeweled(activity=bejeweled_activity):
    command = 'adb shell am start -n {}'.format(activity)
    os.system(command)

def screenshot(intermediate_name='bejeweled'):
    sdcard_directory = '/sdcard/bejeweled_player'
    sdcard_filename = '{}/{}.png'.format(sdcard_directory, intermediate_name)
    now = datetime.now()
    local_filename = 'data/{}-{}.png'.format(intermediate_name, 
            now.strftime("%Y-%m-%d-%H-%M-%S"))
    commands = [
        'adb shell mkdir -p {}'.format(sdcard_directory),
        'adb shell screencap -p {}'.format(sdcard_filename),
        'adb pull {} {}'.format(sdcard_filename, local_filename),
    ]
    for command in commands:
        os.system(command)
    return local_filename

def tap(point):
    pixel = tap_pixel(point.xy)
    command = 'adb shell input tap {0[0]:d} {0[1]:d}'.format(point.xy)
    os.system(command)

def swipe(start_point, end_point, time=100):
    start_pixel = tap_pixel(start_point.xy)
    end_pixel = tap_pixel(end_point.xy)
    command = 'adb shell input swipe {0[0]:d} {0[1]:d} {1[0]:d} {1[1]:d}'.format(start_pixel, end_pixel)
    os.system(command)

if __name__ == '__main__':
    screenshot()

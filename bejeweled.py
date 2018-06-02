#!/usr/bin/env python3

import os
import time
import random

count = (8, 8)

class Point:

    offset = (0, 407)
    size = (1080, 1080)
    one_size = [round(s / c) for (s, c) in zip(size, count)]

    def __init__(self, xyi):
        self.xyi = xyi;
        self.xy = tuple(
                self.offset[i] + round((xyi[i] + 0.5) * self.one_size[i]) 
                for i in range(2))

    def __str__(self):
        return str(self.xyi)

    def __repr__(self):
        return repr(self.xyi)

    def has_left(self):
        return (self.xyi[0] - 1) in range(count[0])

    def has_right(self):
        return (self.xyi[0] + 1) in range(count[0])

    def has_above(self):
        return (self.xyi[1] - 1) in range(count[1])

    def has_below(self):
        return (self.xyi[1] + 1) in range(count[1])

    def left(self):
        return Point((self.xyi[0] - 1, self.xyi[1]))

    def right(self):
        return Point((self.xyi[0] + 1, self.xyi[1]))

    def above(self):
        return Point((self.xyi[0], self.xyi[1] - 1))

    def below(self):
        return Point((self.xyi[0], self.xyi[1] + 1))

    def around(self):
        points = []
        if self.has_left():
            points.append(self.left())
        if self.has_right():
            points.append(self.right())
        if self.has_above():
            points.append(self.above())
        if self.has_below():
            points.append(self.below())
        return points

xyis = [(xi, yi) for xi in range(count[0]) for yi in range(count[1])]
points = { xyi : Point(xyi) for xyi in xyis }

def tap(point):
    command = 'adb shell input tap {0[0]:d} {0[1]:d}'.format(point.xy)
    os.system(command)

def swipe(point1, point2, time=100):
    command = 'adb shell input swipe {0[0]:d} {0[1]:d} {1[0]:d} {1[1]:d}'.format(point1.xy, point2.xy)
    os.system(command)

if __name__ == '__main__':

    target_xyis = [(xi, yi) for xi in range(8) for yi in range(6)]

    while True:
        start_xyi = random.choice(target_xyis)
        start_point = points[start_xyi]
        end_point = random.choice(start_point.around())
        print('swipe {} => {}'.format(start_point, end_point))
        swipe(start_point, end_point)
        time.sleep(0.05)






#!/usr/bin/env python3

import os
import time
import random
from collections import Counter

import phone
import image

count = (8, 8)
offset = (0, 407)
size = (1080, 1080)
one_size = [round(s / c) for (s, c) in zip(size, count)]

class Params:
    pass

params = Params()
params.count = count
params.offset = offset
params.size = size
params.one_size = one_size

class Point:

    def __init__(self, xyi):
        self.xyi = xyi;
        self.xy = tuple(
                params.offset[i] + round((xyi[i] + 0.5) * params.one_size[i]) 
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

xyis = [(xi, yi) 
        for xi in range(params.count[0]) 
        for yi in range(params.count[1])
]
points = { xyi : Point(xyi) for xyi in xyis }

if __name__ == '__main__':

    phone.start_bejeweled()
    input('Please press ENTER to start playing... ')

    while True:
        image_file = phone.screenshot()
        categories = image.identify_categories(image_file, params)

        counter = Counter(categories.values())
        del counter['土']
        common_cat, _ = counter.most_common(1)[0]

        target_xyis = [xyi 
                for (xyi, cat) in categories.items() 
                if cat == common_cat
        ]

        start_xyi = random.choice(target_xyis)
        start_point = points[start_xyi]
        end_point = random.choice(start_point.around())
        print('swipe {} {} => {}'.format(common_cat, start_point, end_point))
        phone.swipe(start_point, end_point)


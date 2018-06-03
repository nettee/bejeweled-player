#!/usr/bin/env python3

import os
import time
import random
from collections import Counter

import phone
import image

size = (8, 8)

class Point:

    def __init__(self, xy):
        self.xy = xy;

    def __str__(self):
        return str(self.xy)

    def __repr__(self):
        return repr(self.xy)

    def has_left(self):
        return (self.xy[0] - 1) in range(size[0])

    def has_right(self):
        return (self.xy[0] + 1) in range(size[0])

    def has_above(self):
        return (self.xy[1] - 1) in range(size[1])

    def has_below(self):
        return (self.xy[1] + 1) in range(size[1])

    def left(self):
        return Point((self.xy[0] - 1, self.xy[1]))

    def right(self):
        return Point((self.xy[0] + 1, self.xy[1]))

    def above(self):
        return Point((self.xy[0], self.xy[1] - 1))

    def below(self):
        return Point((self.xy[0], self.xy[1] + 1))

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

class Board(dict): 

    def __init__(self):
        for x in range(size[0]):
            for y in range(size[1]):
                xy = (x, y)
                self[xy] = Point(xy)

    def color(self, point):
        return self.categories[point.xy]

    def jewels_around(self, point):
        return [p for p in point.around() if self.categories[p.xy] != '土']

board = Board()

if __name__ == '__main__':

    phone.start_bejeweled()
    input('Please press ENTER to start playing... ')

    while True:
        image_file = phone.screenshot()
        categories = image.identify_categories(image_file)
        board.categories = categories

        targets = [xy
                for xy in board
                if categories[xy] != '土']

        start_point = board[random.choice(targets)]
        print('start point: {} {}'.format(board.color(start_point), start_point))
        jewels_around = board.jewels_around(start_point)
        if len(jewels_around) == 0:
            continue
        end_point = random.choice(jewels_around)

        print('swipe {} {} => {}'.format(board.color(start_point),
            start_point, end_point))
        phone.swipe(start_point, end_point)

        time.sleep(0.1)


#!/usr/bin/env python3

import os
import time
import random
from collections import Counter

import phone
import image

size = (8, 8)

class Point:

    left_ = lambda xy: (xy[0] - 1, xy[1])
    right_ = lambda xy: (xy[0] + 1, xy[1])
    up_ = lambda xy: (xy[0], xy[1] - 1)
    down_ = lambda xy: (xy[0], xy[1] + 1)

    directions = (left_, right_, up_, down_)

    def __init__(self, xy):
        self.xy = xy;

    def __str__(self):
        return str(self.xy)

    def __repr__(self):
        return repr(self.xy)

    def valid(self):
        return all(self.xy[i] in range(size[i]) for i in range(2))

    def new_point(self, direction):
        return Point(direction(self.xy))

    def left(self):
        return self.new_point(Point.left_)

    def right(self):
        return self.new_point(Point.right_)

    def above(self):
        return self.new_point(Point.up_)

    def below(self):
        return self.new_point(Point.down_)

    def around(self):
        candidate_points = [self.new_point(direction) 
                for direction in self.directions]
        return [p for p in candidate_points if p.valid()]

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

        for y in range(size[1]):
            for x in range(size[0]):
                print(categories[(x, y)], end=' ')
            print()

        vertical_same_color_pairs = []
        horizontal_same_color_pairs = []
        for x in range(size[0]):
            for y in range(1, size[1]):
                if categories[(x, y)] != '土' and categories[(x, y)] == categories[(x, y-1)]:
                    vertical_same_color_pairs.append((Point((x, y-1)), Point((x, y))))
        for y in range(size[1]):
            for x in range(1, size[0]):
                if categories[(x, y)] != '土' and categories[(x, y)] == categories[(x-1, y)]:
                    horizontal_same_color_pairs.append((Point((x-1, y)), Point((x, y))))

        swipes = []
        for (point_above, point_below) in vertical_same_color_pairs:
            color = board.color(point_above)
            above_above = point_above.above()
            above_arounds = [above_above.above(), above_above.left(), above_above.right()]
            below_below = point_below.below()
            below_arounds = [below_below.below(), below_below.left(), below_below.right()]
            above_candidates = [p for p in above_arounds if p.valid() and board.color(p) == color]
            below_candidates = [p for p in below_arounds if p.valid() and board.color(p) == color]
            if len(above_candidates) > 0:
                swipes.append((above_above, random.choice(above_candidates), color))
            elif len(below_candidates) > 0:
                swipes.append((below_below, random.choice(below_candidates), color))
        for (point_left, point_right) in horizontal_same_color_pairs:
            color = board.color(point_left)
            left_left = point_left.left()
            left_arounds = [left_left.left(), left_left.above(), left_left.below()]
            right_right = point_right.right()
            right_arounds = [right_right.right(), right_right.above(), right_right.below()]
            left_candidates = [p for p in left_arounds if p.valid() and board.color(p) == color]
            right_candidates = [p for p in right_arounds if p.valid() and board.color(p) == color]
            if len(left_candidates) > 0:
                swipes.append((left_left, random.choice(left_candidates), color))
            elif len(right_candidates) > 0:
                swipes.append((right_right, random.choice(right_candidates), color))

        target_swipes = random.sample(swipes, 5) if len(swipes) > 5 else swipes
        print(target_swipes)

        for start_point, end_point, color in target_swipes:
            print('swipe {} {} => {}'.format(color, start_point, end_point))
            phone.swipe(start_point, end_point)

        time.sleep(0.1)


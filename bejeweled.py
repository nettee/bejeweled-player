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

class Match:

    def __init__(self, slot, target, bases, color):
        self.slot = slot
        self.target = target
        self.bases = bases
        self.color = color


def get_candidate_matches(board):

    categories = board.categories

    vertical_L_bases = []
    horizontal_L_bases = []
    vertical_T_bases = []
    horizontal_T_bases = []

    for x in range(size[0]):
        for y in range(1, size[1]):
            if categories[(x, y)] != '土' and categories[(x, y)] == categories[(x, y-1)]:
                vertical_L_bases.append((Point((x, y-1)), Point((x, y))))
        for y in range(2, size[1]):
            if categories[(x, y)] != '土' and categories[(x, y)] == categories[(x, y-2)]:
                vertical_T_bases.append((Point((x, y-2)), Point((x, y))))
    for y in range(size[1]):
        for x in range(1, size[0]):
            if categories[(x, y)] != '土' and categories[(x, y)] == categories[(x-1, y)]:
                horizontal_L_bases.append((Point((x-1, y)), Point((x, y))))
        for x in range(2, size[0]):
            if categories[(x, y)] != '土' and categories[(x, y)] == categories[(x-2, y)]:
                horizontal_T_bases.append((Point((x-2, y)), Point((x, y))))

    matches = []

    for bases in vertical_L_bases:
        base_above, base_below = bases
        color = board.color(base_above)

        above_above = base_above.above()
        if above_above.valid() and board.color(above_above) != '土':
            above_arounds = [above_above.above(), above_above.left(), above_above.right()]
            above_candidates = [p for p in above_arounds if p.valid() and board.color(p) == color]
            for c in above_candidates:
                match = Match(slot=above_above, target=c, bases=bases, color=color)
                matches.append(match)

        below_below = base_below.below()
        if below_below.valid() and board.color(below_below) != '土':
            below_arounds = [below_below.below(), below_below.left(), below_below.right()]
            below_candidates = [p for p in below_arounds if p.valid() and board.color(p) == color]
            for c in below_candidates:
                match = Match(slot=below_below, target=c, bases=bases, color=color)
                matches.append(match)

    for bases in horizontal_L_bases:
        base_left, base_right = bases
        color = board.color(base_left)

        left_left = base_left.left()
        if left_left.valid() and board.color(left_left) != '土':
            left_arounds = [left_left.left(), left_left.above(), left_left.below()]
            left_candidates = [p for p in left_arounds if p.valid() and board.color(p) == color]
            for c in left_candidates:
                match = Match(slot=left_left, target=c, bases=bases, color=color)
                matches.append(match)

        right_right = base_right.right()
        if right_right.valid() and board.color(right_right) != '土':
            right_arounds = [right_right.right(), right_right.above(), right_right.below()]
            right_candidates = [p for p in right_arounds if p.valid() and board.color(p) == color]
            for c in right_candidates:
                match = Match(slot=right_right, target=c, bases=bases, color=color)
                matches.append(match)

    for bases in vertical_T_bases:
        base_above, base_below = bases
        color = board.color(base_above)
        middle = base_above.below()
        if middle.valid() and board.color(middle) != '土':
            candidates = [middle.left(), middle.right()]
            for c in candidates:
                match = Match(slot=middle, target=c, bases=bases, color=color)
                matches.append(match)

    for bases in horizontal_T_bases:
        base_left, base_right = bases
        color = board.color(base_left)
        middle = base_left.right()
        if middle.valid() and board.color(middle) != '土':
            candidates = [middle.above(), middle.below()]
            for c in candidates:
                match = Match(slot=middle, target=c, bases=bases, color=color)
                matches.append(match)

    return matches


def select_matches(board, matches):
    sorted_matches = sorted(matches, key=lambda m: m.slot.xy[1], reverse=True)
    target_matches = sorted_matches[:5] if len(sorted_matches) > 5 else sorted_matches
    return target_matches


if __name__ == '__main__':

    phone.start_bejeweled()
    input('Please press ENTER to start playing... ')

    board = Board()

    while True:
        image_file = phone.screenshot()
        categories = image.identify_categories(image_file)
        board.categories = categories

        candidate_matches = get_candidate_matches(board)

        for y in range(size[1]):
            for x in range(size[0]):
                print(categories[(x, y)], end=' ')
            print()

        target_matches = select_matches(board, candidate_matches)
        print(target_matches)

        for match in target_matches:
            print('swipe {} {} => {}'.format(match.color, match.slot, match.target))
            phone.swipe(match.slot, match.target)

        time.sleep(0.1)


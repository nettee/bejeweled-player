#!/usr/bin/env python3

import sys
import time
import random

import color
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

    def colorful(self, point):
        return self.color(point) != color.EARTH

    def jewels_around(self, point):
        return [p for p in point.around() if self.colorful(p)]

class Match:

    def __init__(self, slot, target, bases, color):
        self.slot = slot
        self.target = target
        self.bases = bases
        self.color = color

    @property
    def eliminate_places(self):
        return (self.slot, self.bases[0], self.bases[1])

    @property
    def min_x(self):
        return min(p.xy[0] for p in self.eliminate_places)

    @property
    def min_y(self):
        return min(p.xy[1] for p in self.eliminate_places)

    @property
    def max_x(self):
        return max(p.xy[0] for p in self.eliminate_places)

    @property
    def max_y(self):
        return max(p.xy[1] for p in self.eliminate_places)


def get_candidate_matches(board, log_file=None):

    categories = board.categories

    vertical_L_bases = []
    horizontal_L_bases = []
    vertical_T_bases = []
    horizontal_T_bases = []

    for x in range(size[0]):
        for y in range(1, size[1]):
            if categories[(x, y)] != color.EARTH and categories[(x, y)] == categories[(x, y-1)]:
                vertical_L_bases.append((Point((x, y-1)), Point((x, y))))
        for y in range(2, size[1]):
            if categories[(x, y)] != color.EARTH and categories[(x, y)] == categories[(x, y-2)]:
                vertical_T_bases.append((Point((x, y-2)), Point((x, y))))
    for y in range(size[1]):
        for x in range(1, size[0]):
            if categories[(x, y)] != color.EARTH and categories[(x, y)] == categories[(x-1, y)]:
                horizontal_L_bases.append((Point((x-1, y)), Point((x, y))))
        for x in range(2, size[0]):
            if categories[(x, y)] != color.EARTH and categories[(x, y)] == categories[(x-2, y)]:
                horizontal_T_bases.append((Point((x-2, y)), Point((x, y))))

    def find_matches(base, slot_relatives, target_relatives):
        assert(len(slot_relatives) == len(target_relatives))
        color = board.color(base[0])
        for slot_rel, targets_rel in zip(slot_relatives, target_relatives):
            slot = slot_rel(base)
            if not slot.valid() or not board.colorful(slot):
                continue
            targets = targets_rel(slot)
            for target in targets:
                if not target.valid() or not board.color(target):
                    continue
                if board.color(target) == color:
                    match = Match(slot=slot, target=target, bases=base, color=color)
                    yield match

    match_patterns = [
        (
            vertical_L_bases,
            [lambda base: base[0].above(),
             lambda base: base[1].below()],
            [lambda slot: (slot.above(), slot.left(), slot.right()),
             lambda slot: (slot.below(), slot.left(), slot.right())]
        ),
        (
            vertical_T_bases,
            [lambda base: base[0].below()],
            [lambda slot: (slot.left(), slot.right())]
        ),
        (
            horizontal_L_bases,
            [lambda base: base[0].left(),
             lambda base: base[1].right()],
            [lambda slot: (slot.left(), slot.above(), slot.below()),
             lambda slot: (slot.right(), slot.above(), slot.below())]
        ),
        (
            horizontal_T_bases,
            [lambda base: base[0].right()],
            [lambda slot: (slot.above(), slot.below())]
        ),
    ]

    matches = []

    for bases, slot_relatives, target_relatives in match_patterns:
        for base in bases:
            matches_gen = find_matches(base, slot_relatives, target_relatives)
            for m in matches_gen:
                matches.append(m)

    return matches


def select_matches(board, matches):
    # sorted_matches = sorted(matches, key=lambda m: m.slot.xy[1], reverse=True)
    # target_matches = sorted_matches[:5] if len(sorted_matches) > 5 else sorted_matches
    target_matches = random.sample(matches, 5) if len(matches) > 5 else matches
    return target_matches


if __name__ == '__main__':

    phone.start_bejeweled()
    input('Please press ENTER to start playing... ')

    board = Board()

    while True:
        image_file = phone.screenshot()
        categories = image.identify_categories(image_file)
        board.categories = categories

        log_file = open(image_file + '.log', 'w')

        candidate_matches = get_candidate_matches(board, log_file=log_file)

        for y in range(size[1]):
            for x in range(size[0]):
                print(categories[(x, y)], end=' ', file=log_file)
            print(file=log_file)

        target_matches = select_matches(board, candidate_matches)
        print(target_matches, file=sys.stdout)
        print(target_matches, file=log_file)

        for match in target_matches:
            print('swipe {} {} => {}'.format(match.color, match.slot, match.target), file=sys.stdout)
            print('swipe {} {} => {}'.format(match.color, match.slot, match.target), file=log_file)
            phone.swipe(match.slot, match.target)

        log_file.close()

        time.sleep(0.1)


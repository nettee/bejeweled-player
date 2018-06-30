#!/usr/bin/env python3

import time
from datetime import datetime
import threading
from pathlib import Path

import numpy as np

from jinja2 import Environment, FileSystemLoader

import color
import image
import phone

size = (8, 8)


log_dir = Path('log')
if not log_dir.exists():
    log_dir.mkdir()


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

    def first_earth(self, x):
        for y in range(size[1]):
            if self.categories[(x, y)] == color.EARTH:
                return y
        else:
            return size[1]

    def situation(self, categories):
        self.categories = categories
        self.baseline = [self.first_earth(x) for x in range(size[0])]

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


y_weights = {
    0: 0.1,
    1: 0.2,
    2: 0.3,
    3: 0.4,
    4: 0.6,
    5: 0.8,
    6: 0.7,
    7: 0.6,
}


def weigh(board, match):
    return y_weights[match.max_y]


def select_matches(board, matches, choice_size=4):
    if len(matches) <= choice_size:
        return matches

    weights = [weigh(board, m) for m in matches]
    weights_sum = sum(weights)
    probs = [w / weights_sum for w in weights]

    a = np.arange(len(matches))
    indices = np.random.choice(a, choice_size, replace=False, p=probs)
    return [matches[i] for i in indices]


# Shared variable
working = True


def main():
    board = Board()

    now = datetime.now()
    log_file = open('log/{}.html'.format(now.strftime("%Y-%m-%d-%H-%M-%S")), 'w')

    start_file = open('templates/start.html')
    print(start_file.read(), file=log_file)
    start_file.close()

    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template('logitem.html')

    while working:
        image_file = phone.screenshot()
        categories = image.identify_categories(image_file)
        board.situation(categories)

        candidate_matches = get_candidate_matches(board, log_file=log_file)

        target_matches = select_matches(board, candidate_matches)

        for match in target_matches:
            phone.swipe(match.slot, match.target)

        data = {
            'image_file': '../' + image_file,
            'colors': categories,
            'target_matches': target_matches,
        }
        print(template.render(**data), file=log_file)

        time.sleep(0.1)

    print('Stops working.')

    end_file = open('templates/end.html')
    print(end_file.read(), file=log_file)
    end_file.close()
    log_file.close()


if __name__ == '__main__':

    phone.start_bejeweled()
    input('Please press ENTER to start playing... ')

    t = threading.Thread(target=main, name='MainThread')
    t.start()

    input('Please press ENTER to end playing...')
    working = False
    t.join()
    print('Bye.')




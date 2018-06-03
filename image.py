#!/usr/bin/env python3

import colorsys

from PIL import Image

board_resolution = (1080, 1080)
board_offset = (0, 407)
board_size = (8, 8)
jewel_resolution = tuple(round(s / c)
        for (s, c) in zip(board_resolution, board_size))

def average_hue(image):
    hues = [colorsys.rgb_to_hsv(*image.getpixel((x, y)))[0]
        for x in range(image.size[0]) 
        for y in range(image.size[1])
    ]
    avg_hue = sum(hues) / len(hues)
    return avg_hue

def get_category(image):
    hue = average_hue(image)
    if hue > 0.8976:
        return '红'
    elif hue > 0.5931:
        return '紫'
    elif hue > 0.3320:
        return '绿'
    elif hue > 0.2226:
        return '白'
    elif hue > 0.1379:
        return '黄'
    else:
        return '土'

def identify_categories(image_filename):

    xys = [(x, y)
            for x in range(board_size[0])
            for y in range(board_size[1])
    ]
    upper_lefts = { xy: 
        [board_offset[i] + xy[i] * jewel_resolution[i] for i in range(2)]
        for xy in xys
    }
    bottom_rights = { xy: 
        [board_offset[i] + (xy[i] + 1) * jewel_resolution[i] for i in range(2)]
        for xy in xys
    }
    boxes = { xy:
        tuple(upper_lefts[xy] + bottom_rights[xy])
        for xy in xys
    }

    image = Image.open(image_filename)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    categories = {}
    for ((x, y), box) in boxes.items():
        region = image.crop(box)
        center = region.crop((45, 45, 90, 90))
        cat = get_category(center)
        categories[(x, y)] = cat

    return categories


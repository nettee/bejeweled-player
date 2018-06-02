#!/usr/bin/env python3

import colorsys

from PIL import Image

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

def identify_categories(image_filename, params):

    count = params.count
    offset = params.offset
    one_size = params.one_size

    xyis = [(xi, yi)
            for xi in range(count[0])
            for yi in range(count[1])
    ]
    upper_lefts = { xyi: 
        [offset[i] + xyi[i] * one_size[i] for i in range(2)]
        for xyi in xyis
    }
    bottom_rights = { xyi: 
        [offset[i] + (xyi[i] + 1) * one_size[i] for i in range(2)]
        for xyi in xyis
    }
    boxes = { xyi:
        tuple(upper_lefts[xyi] + bottom_rights[xyi])
        for xyi in xyis
    }

    image = Image.open(image_filename)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    categories = {}
    for ((xi, yi), box) in boxes.items():
        region = image.crop(box)
        center = region.crop((45, 45, 90, 90))
        cat = get_category(center)
        categories[(xi, yi)] = cat

    return categories


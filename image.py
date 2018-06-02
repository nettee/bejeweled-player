#!/usr/bin/env python3

from PIL import Image

def crop(image_filename, params):

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
    for ((xi, yi), box) in boxes.items():
        region = image.crop(box)
        region.save('bejeweled-cropped-{}-{}.png'.format(xi, yi))


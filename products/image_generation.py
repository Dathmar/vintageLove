from pathlib import Path
import os
import sys

sys.path.append(Path(__file__).resolve().parent.parent)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vintageLove.settings")


import django
django.setup()

from products.models import ProductImage
from PIL import Image


def gen_resize(infile, max_size):
    with Image.open(infile) as im:
        new_size = get_new_image_size(max_size, (im.width, im.height))
        im_resized = im.resize(new_size)

    return im_resized


def get_new_image_size(max_size, image_size):
    # if the width is greater than height
    # then ratio should be to width else height
    if image_size[0] > image_size[1]:
        ratio = max_size[0] / image_size[0]
    else:
        ratio = max_size[1] / image_size[1]

    return (int(image_size[0] * ratio), int(image_size[1] * ratio))


if __name__ == "__main__":

    for pImage in ProductImage.objects.all():
        media_dir = Path(__file__).resolve().parent.parent
        image_location = str(media_dir).replace('\\', '/') + repr(pImage)
        print(image_location)
        img = Image.open(image_location)
        new_img = gen_resize(image_location, (500, 400))

        new_img.save(image_location, img.format)

        pImage.image_height = new_img.height
        pImage.image_width = new_img.width
        pImage.save()

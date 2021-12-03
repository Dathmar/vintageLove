'''from pathlib import Path
import os
import sys

sys.path.append(Path(__file__).resolve().parent.parent)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vintageLove.settings")


import django
django.setup()

from products.models import ProductImage'''
from PIL import Image
import piexif


def rotate_image(img):
    if "exif" in img.info:
        exif_dict = piexif.load(img.info["exif"])

        if piexif.ImageIFD.Orientation in exif_dict["0th"]:
            orientation = exif_dict["0th"].pop(piexif.ImageIFD.Orientation)
            exif_bytes = piexif.dump(exif_dict)
            if orientation == 2:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                img = img.rotate(180)
            elif orientation == 4:
                img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 5:
                img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                img = img.rotate(-90, expand=True)
            elif orientation == 7:
                img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                img = img.rotate(90, expand=True)

    return img


def gen_resize(infile, max_size):
    with Image.open(infile) as im:
        rotated = rotate_image(im)

    new_size = get_new_image_size(max_size, (rotated.width, rotated.height))
    im_resized = rotated.resize(new_size, Image.ANTIALIAS)

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
    img = 'test.jpeg'
    new_image = gen_resize(img, (300, 300))

    new_image.save('test2', format)


'''if __name__ == "__main__":

    for pImage in ProductImage.objects.all():
        media_dir = Path(__file__).resolve().parent.parent
        image_location = str(media_dir).replace('\\', '/') + repr(pImage)
        print(image_location)
        img = Image.open(image_location)
        new_img = gen_resize(image_location, (500, 400))

        new_img.save(image_location, img.format)

        pImage.image_height = new_img.height
        pImage.image_width = new_img.width
        pImage.save()'''


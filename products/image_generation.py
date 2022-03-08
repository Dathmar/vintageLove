from PIL import Image
import piexif

import logging

logger = logging.getLogger('app_api')

def rotate_image(img_path):
    with Image.open(img_path) as im:
        img = im.copy()

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

        img.save(img_path)
        img.close()


def gen_resize(infile, max_size):
    with Image.open(infile) as im:
        img = im.copy()

    new_size = get_new_image_size(max_size, (img.width, img.height))
    im_resized = img.resize(new_size, Image.ANTIALIAS)

    return im_resized


def get_new_image_size(max_size, image_size):
    # if the width is greater than height
    # then ratio should be to width else height
    if image_size[0] > image_size[1]:
        ratio = max_size[0] / image_size[0]
    else:
        ratio = max_size[1] / image_size[1]

    return (int(image_size[0] * ratio), int(image_size[1] * ratio))


'''if __name__ == "__main__":
    img = 'test.jpeg'
    new_image = gen_resize(img, (300, 300))

    new_image.save('test2', format)'''






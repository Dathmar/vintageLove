from PIL import Image
import sys
import os


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
    check_dir = r'C:\Users\ADANNER\PycharmProjects\vintageLove\media\product_images'

    for infile in os.listdir(check_dir):
        if infile.endswith(".png"):
            new_img = gen_resize(os.path.join(check_dir, infile), (128, 128))
            filename = os.path.splitext(infile)[0]
            print(os.path.join(check_dir, filename + '.png'))

            new_img.save(os.path.join(check_dir, 'test', filename + '.png'), 'PNG')

from pathlib import Path
import os
import sys
import django

from PIL import Image

print(Path(__file__).resolve().parent.parent)
sys.path.append(Path(__file__).resolve().parent.parent)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vintageLove.settings")

if not hasattr(django, 'apps'):
    django.setup()

from django.conf import settings
from products.image_generation import gen_resize
from products.models import ProductImage

def do_resize():
    for pImage in ProductImage.objects.filter(image_size=0):
        media_dir = settings.MEDIA_ROOT
        image_path = os.path.join(media_dir, pImage.image.name)
        img = Image.open(image_path)
        new_img = gen_resize(image_path, (500, 400))

        new_img_path = os.path.join('product_images/thumbnail/',
                                    os.path.basename(pImage.image.path))
        new_img.save(os.path.join(settings.MEDIA_ROOT, new_img_path))

        new_img.save(image_path, img.format)

        new_image = ProductImage.objects.create(
            product=pImage.product,
            image_size=1,
            image=new_img_path,
            sequence=pImage.sequence,
        )

def do_resequence():
    product_dup_images = []
    for pImage in ProductImage.objects.filter(image_size=0):
        if ProductImage.objects.filter(product=pImage.product,
                                       image_size=0,
                                       sequence=pImage.sequence).count() > 1:

            if pImage.product not in product_dup_images:
                product_dup_images.append(pImage.product)

    print(product_dup_images)
    for i, prod in enumerate(product_dup_images):
        img_count = 1
        for dImage in ProductImage.objects.filter(product=prod, image_size=0).order_by('sequence'):
            print(prod)
            dImage.sequence = img_count
            dImage.save()
            image_base_name = os.path.basename(dImage.image.path)
            tImage = ProductImage.objects.get(
                product=dImage.product,
                image_size=1,
                image__iendswith=image_base_name,
            )
            tImage.sequence = img_count
            tImage.save()

            img_count += 1


if __name__ == "__main__":
    do_resequence()

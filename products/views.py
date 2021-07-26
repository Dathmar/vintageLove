from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductImage, UserSeller, ProductStatus
from datetime import datetime


# Create your views here.
def product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_images = ProductImage.objects.filter(product_id=product_id).order_by('sequence')

    is_seller = False
    if request.user.is_authenticated:
        is_seller = UserSeller.objects.filter(user=request.user, seller=product.seller_id).exists()

    context = {
        'product': product,
        'product_images': product_images,
        'is_seller': is_seller,
    }
    return render(request, 'product-page.html', context)


def product_sold(request, product_id):
    product_to_update = get_object_or_404(Product, pk=product_id)

    if request.user.is_authenticated and UserSeller.objects.filter(user=request.user,
                                                                   seller=product_to_update.seller_id).exists():
        sold_status = ProductStatus.objects.filter(name='Sold').first()
        product_to_update.status = sold_status
        product_to_update.update_datetime = datetime.now()
        product_to_update.save()

    return product(request, product_id)


def product_image(request, product_id, sequence):
    image = get_object_or_404(ProductImage, product_id=product_id, sequence=sequence)

    context = {
        'image': image,
    }
    return render(request, 'product_image.html', context)


def product_qr(request, product_id):
    context = {
        'product_id': product_id,
    }
    return render(request, 'product-qr.html', context)


def product_list(request):
    products = Product.objects.filter(status__name='Available')

    context = {
        'products': products,
    }

    return render(request, 'product-list.html', context)

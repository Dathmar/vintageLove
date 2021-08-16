from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, ProductImage, UserSeller, ProductStatus, Category
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


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    product_lst = Product.objects.filter(status__name='Available',
                                         productimage__sequence=1)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        product_lst = product_lst.filter(category=category)

    attributes = product_lst.values('attributes')

    merged_attributes = {}
    for attribute in attributes:
        for i, (key, value_list) in enumerate(attribute['attributes'].items()):
            if key not in merged_attributes:
                merged_attributes[key] = value_list.copy()
            else:
                for value in value_list:
                    if value not in merged_attributes[key]:
                        merged_attributes[key].append(value)


    product_lst_values = product_lst.values('id', 'title', 'description', 'retail_price', 'productimage__image',
                                            'productimage__image_height', 'productimage__image_width')

    products = make_pages(request, product_lst_values, 10)

    context = {
        'products': products,
        'attributes': attributes,
        'merged_attributes': merged_attributes,
    }

    return render(request, 'product-list-cards.html', context)


def make_pages(request, obj_to_page, page_size):
    page = request.GET.get('page', 1)
    paginator = Paginator(obj_to_page, page_size)
    try:
        paged_obj = paginator.page(page)
    except PageNotAnInteger:
        paged_obj = paginator.page(1)
    except EmptyPage:
        paged_obj = paginator.page(paginator.num_pages)

    return paged_obj

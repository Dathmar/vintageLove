from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, ProductImage, UserSeller, ProductStatus, Category
from datetime import datetime
from .merged_attributes import get_attribute_list
from django.db.models import Max, Min


# Create your views here.
def product(request, product_id):
    item = Product.objects.get(pk=product_id)
    return redirect('products:product-slug', item.slug)


def product_slug(request, product_slug):
    item = Product.objects.get(slug=product_slug)
    context = get_product_context(request, product_slug)

    similar_products = Product.objects.filter(category=item.category).exclude(id=item.id)[:5]

    context.update({'similar_products': similar_products})

    return render(request, 'product-page.html', context)


def get_product_context(request, product_identifier, identifier_type='slug'):
    product = get_object_or_404(Product, slug=product_identifier)

    product_images = ProductImage.objects.filter(product_id=product.pk).order_by('sequence')

    is_seller = False
    if request.user.is_authenticated:
        is_seller = UserSeller.objects.filter(user=request.user, seller=product.seller_id).exists()

    return {
        'product': product,
        'product_images': product_images,
        'is_seller': is_seller,
    }


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


def product_qr_list(request):
    products = Product.objects.get()
    context = {
        'products': products,
    }

    return render(request, 'product-qr-list.html', context)


def product_qr_grid(request):
    products = Product.objects.filter().order_by('-create_datetime')
    context = {
        'products': products,
    }

    return render(request, 'product-qr-grid.html', context)




def product_list(request, category_slug=None):
    product_lst = Product.objects.filter(status__name='Available',
                                         productimage__sequence=1)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        product_lst = product_lst.filter(category=category)

    attributes = product_lst.values('attributes')

    product_lst_values = product_lst.values('id', 'title', 'description', 'retail_price', 'productimage__image',
                                            'productimage__image_height', 'productimage__image_width')

    prices = product_lst.aggregate(Min('retail_price')).update(product_lst.aggregate(Max('retail_price')))

    products = make_pages(request, product_lst_values, 12)

    context = {
        'prices': prices,
        'products': products,
        'attributes': get_attribute_list(attributes),
    }

    return render(request, 'product-list.html', context)


def product_list_update(request, category_slug=None):
    product_lst = Product.objects.filter(status__name='Available').order_by('-create_datetime')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        product_lst = product_lst.filter(category=category)

    attributes = product_lst.values('attributes')
    prices = product_lst.aggregate(Min('retail_price')).update(product_lst.aggregate(Max('retail_price')))

    product_pages = make_pages(request, product_lst.values('id'), 12)
    product_images = ProductImage.objects.filter(product_id__in=list(x['id'] for x in product_pages.object_list))

    products = product_images.values('product__id', 'product__title', 'product__description',
                                     'product__retail_price', 'image')

    context = {
        'prices': prices,
        'product_pages': product_pages,
        'products': products,
        'attributes': get_attribute_list(attributes),
    }

    return render(request, 'product-list.html', context)


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

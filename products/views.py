from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, ProductImage, UserSeller, ProductStatus, Category
from datetime import datetime
from .merged_attributes import get_attribute_list
from django.db.models import Max, Min


# Create your views here.
def product(request, product_id):
    item = Product.objects.get(pk=product_id)
    return redirect('products:product-slug', item.slug)


def product_w_slug(request, product_slug):
    item = Product.objects.get(slug=product_slug)
    context = get_product_context(request, product_slug)

    similar_products = Product.objects.filter(
        productcategory__category__in=list(x.category for x in item.productcategory_set.all())
    ).exclude(id=item.id)[:5]

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
    product_lst = Product.objects.filter(status__available_to_sell=True).order_by('-create_datetime')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        product_lst = product_lst.filter(productcategory__category=category)

    price_min = request.GET.get('priceMin')
    price_max = request.GET.get('priceMax')

    if price_min and price_max:
        if price_min > price_max:
            tmp = price_max
            price_max = price_min
            price_min = tmp

        product_lst = product_lst.filter(retail_price__range=(price_min, price_max))
    elif price_min:
        product_lst = product_lst.filter(retail_price__gte=price_min)
    elif price_max:
        product_lst = product_lst.filter(retail_price__lte=price_max)

    attributes = product_lst.values('attributes')
    prices = product_lst.aggregate(Min('retail_price')).update(product_lst.aggregate(Max('retail_price')))

    product_pages = make_pages(request, product_lst.values('id'), 12)

    products = product_pages.object_list.values('id', 'title', 'retail_price', 'slug')

    for product in products:
        images = []
        url = reverse('products:product-slug', kwargs={'product_slug': product['slug']})
        product_images = ProductImage.objects.filter(product__id=product['id']).order_by('sequence')
        for product_image in product_images:
            images.append(product_image)

        product.update({'images': images, 'url': url})

    context = {
        'prices': prices,
        'product_pages': product_pages,
        'products': products,
        'attributes': get_attribute_list(attributes),
    }

    return render(request, 'product-list.html', context)


def product_list_stage(request, stage):
    product_lst = Product.objects.filter(status__available_to_sell=True).order_by('-create_datetime')

    if stage:
        product_lst = product_lst.filter(status__name__iexact=stage)

    price_min = request.GET.get('priceMin')
    price_max = request.GET.get('priceMax')

    if price_min and price_max:
        if price_min > price_max:
            tmp = price_max
            price_max = price_min
            price_min = tmp

        product_lst = product_lst.filter(retail_price__range=(price_min, price_max))
    elif price_min:
        product_lst = product_lst.filter(retail_price__gte=price_min)
    elif price_max:
        product_lst = product_lst.filter(retail_price__lte=price_max)

    attributes = product_lst.values('attributes')
    prices = product_lst.aggregate(Min('retail_price')).update(product_lst.aggregate(Max('retail_price')))

    product_pages = make_pages(request, product_lst.values('id'), 12)

    products = product_pages.object_list.values('id', 'title', 'retail_price', 'slug')

    for product in products:
        images = []
        url = reverse('products:product-slug', kwargs={'product_slug': product['slug']})
        product_images = ProductImage.objects.filter(product__id=product['id']).order_by('sequence')
        for product_image in product_images:
            images.append(product_image)

        product.update({'images': images, 'url': url})

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

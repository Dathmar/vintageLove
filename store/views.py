from django.shortcuts import render
from products.models import Category, Product, ProductImage


# Create your views here.
def index(request):
    categories = Category.objects.all().order_by('id')

    product_lst = Product.objects.filter(status__name='Available',
                                         productimage__sequence=1).order_by("-create_datetime")
    product_lst = product_lst[:12]

    products = product_lst.values('id', 'title', 'retail_price')

    for product in products:
        images = []
        product_images = ProductImage.objects.filter(product__id=product['id'])
        for product_image in product_images:
            images.append(product_image)

        product.update({'images': images, })

    context = {
        'categories':  categories,
        'products': products
    }
    return render(request, 'index.html', context)


def our_purpose(request):
    return render(request, 'our-purpose.html')


def our_purpose_retail(request):
    return render(request, 'our-purpose-retail.html')


def join_movement(request):
    return render(request, 'join-movement.html')


def privacy_policy(request):
    return render(request, 'privacy-policy.html')


def return_policy(request):
    return  render(request, 'return-policy.html')

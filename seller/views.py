from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.contrib.auth.decorators import login_required

from products.models import UserSeller, Product, ProductImage, ProductCategory, Category, ProductStatus
from .forms import ProductForm

# Create your views here.
@login_required(login_url='/login/')
def product_list(request):
    user_sellers = get_list_or_404(UserSeller, user=request.user)
    sellers = []
    for seller in user_sellers:
        sellers.append(seller.seller)

    products = Product.objects.filter(seller__in=sellers).all()

    context = {
        'seller': seller,
        'products': products,
    }
    return render(request, 'seller-product-list.html', context=context)


@login_required(login_url='/login/')
def add_product(request):
    product_form = ProductForm()
    user_sellers = get_list_or_404(UserSeller, user=request.user)

    sellers = []
    for seller in user_sellers:
        sellers.append(seller.seller)

    multi_seller = False
    if len(sellers) > 1:
        multi_seller = True
    context = {
        'multi_seller': multi_seller,
        'seller': seller,
        'product_form': product_form,
    }
    return render(request, 'seller-add-product.html', context=context)


@login_required(login_url='/login/')
def edit_product(request, product_id):
    user_sellers = get_list_or_404(UserSeller, user=request.user)
    sellers = []
    for seller in user_sellers:
        sellers.append(seller.seller)

    product = get_object_or_404(Product, id=product_id, seller__in=sellers)
    context = {
        'product': product,
    }
    return render(request, 'seller-edit-product.html', context=context)

from django.shortcuts import render, get_list_or_404, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.utils.html import mark_safe
from django.forms import formset_factory

from products.models import UserSeller, Product, ProductImage, ProductCategory, Category
from .forms import ProductForm, ProductImageForm, ProductCategoryForm


# Create your views here.
@login_required(login_url='/accounts/login/')
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


@login_required(login_url='/accounts/login/')
def add_product(request):
    user_sellers = get_list_or_404(UserSeller, user=request.user)
    sellers = ""
    seller_list = []
    for seller in user_sellers:
        sellers += "'" + seller.seller.name + "',"
        seller_list.append(seller.seller)

    sellers = mark_safe("[" + sellers[:-1] + "]")

    if request.method == 'POST':
        ImageFormset = formset_factory(ProductImageForm)
        CategoryFormset = formset_factory(ProductCategoryForm)

        product_form = ProductForm(request.POST)
        image_formset = ImageFormset(request.POST, request.FILES)
        category_formset = CategoryFormset(request.POST)

        if product_form.is_valid() and image_formset.is_valid() and category_formset.is_valid():
            product = Product.objects.create(
                title=product_form.cleaned_data['title'],
                description=product_form.cleaned_data['description'],
                seller=seller_list[int(product_form.cleaned_data['seller'])],
                dimension_width=product_form.cleaned_data['dimension_width'],
                dimension_height=product_form.cleaned_data['dimension_height'],
                dimension_length=product_form.cleaned_data['dimension_length'],
                dimension_weight=product_form.cleaned_data['dimension_weight'],
                purchase_price=product_form.cleaned_data['purchase_price'],
                wholesale_price=product_form.cleaned_data['wholesale_price'],
                retail_price=product_form.cleaned_data['retail_price'],
                origin=product_form.cleaned_data['origin'],
            )
            product.save()

            count = 1
            for image_form in image_formset:
                if image_form.cleaned_data.get('image'):
                    product_image = ProductImage.objects.create(
                        product=product,
                        image=image_form.cleaned_data.get('image'),
                        sequence=count,
                    )
                    product_image.save()
                    count += 1

            for category in category_formset:
                if category.cleaned_data.get('category'):
                    product_category = ProductCategory.objects.create(
                        product=product,
                        category=Category.objects.get(id=int(category.cleaned_data.get('category'))),
                    )
                    product_category.save()

            return product_list(request)
        else:

            context = {
                'sellers': sellers,
                'product_form': product_form,
                'image_formset': image_formset,
                'category_formset': category_formset,
            }
            return render(request, 'seller-add-product.html', context=context)

    ImageFormset = formset_factory(ProductImageForm, extra=4)
    CategoryFormset = formset_factory(ProductCategoryForm, extra=3)

    product_form = ProductForm()
    image_formset = ImageFormset()
    category_formset = CategoryFormset()
    context = {
        'sellers': sellers,
        'product_form': product_form,
        'image_formset': image_formset,
        'category_formset': category_formset,
    }
    return render(request, 'seller-add-product.html', context=context)


@login_required(login_url='/accounts/login/')
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

from django.shortcuts import render, reverse
from products.models import Category, Product, ProductImage
from django.http.response import JsonResponse
from django.conf import settings
import mailchimp_marketing as mailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
import json


# Create your views here.
def index(request):
    categories = Category.objects.all().order_by('id')

    product_lst = Product.objects.filter(status__available_to_sell=True,
                                         productimage__sequence=1).order_by("-create_datetime")
    product_lst = product_lst[:12]

    products = product_lst.values('id', 'title', 'retail_price',
                                                'wholesale_price', 'status__disply_wholesale', 'slug')

    for product in products:
        images = []
        url = reverse('products:product-slug', kwargs={'product_slug': product['slug']})
        product_images = ProductImage.objects.filter(product__id=product['id']).order_by('sequence')
        for product_image in product_images:
            images.append(product_image)

        product.update({'images': images, 'url': url})

    context = {
        'categories':  categories,
        'products': products,
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


def marketing_signup(request):
    if request.method == 'POST':
        mailchimp = mailchimpMarketing.Client()
        mailchimp.set_config({
            "api_key": settings.MAILCHIMP_API_KEY,
            "server": settings.MAILCHIMP_SERVER
        })

        list_id = settings.MAILCHIMP_MARKETING_LIST_ID

        member_info = {
            "email_address": json.loads(request.body)['email'],
            "status": "pending",
        }

        try:
            response = mailchimp.lists.add_list_member(list_id, member_info)
            data = {
                "status": "success",
                "response": response,
            }
        except ApiClientError as error:
            data = {
                "status": "error",
                "response": json.loads(error.text),
            }

        return JsonResponse(data)

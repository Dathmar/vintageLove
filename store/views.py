from django.shortcuts import render, reverse, HttpResponseRedirect
from products.models import Category, Product, ProductImage, HomepageProducts
from django.http.response import JsonResponse
from django.conf import settings
from .forms import JoinMovement

from base.Emailing import EmailThread

import mailchimp_marketing as mailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
import json


# Create your views here.
def index(request):
    categories = Category.objects.all().order_by('id')

    product_lst = Product.objects.filter(status__available_to_sell=True,
                                         productimage__sequence=1,
                                         productimage__image_size=1,
                                         pk__in=HomepageProducts.objects.all().order_by('sequence').values('product_id')
                                         )
    product_lst = product_lst[:12]

    products = product_lst.values('id', 'title', 'retail_price',
                                  'wholesale_price', 'status__display_wholesale', 'slug')

    for product in products:
        images = []
        url = reverse('products:product-slug', kwargs={'product_slug': product['slug']})
        product_images = ProductImage.objects.filter(product__id=product['id'], image_size=1).order_by('sequence')
        for product_image in product_images:
            images.append(product_image)

        product.update({'images': images, 'url': url})

    context = {
        'categories':  categories,
        'products': products,
    }
    return render(request, 'index.html', context)


def storage(request):
    return render(request, 'store-page.html')


def test(request):
    product_lst = Product.objects.filter(status__available_to_sell=True,
                                         productimage__sequence=1,
                                         productimage__image_size=1,
                                         pk__in=HomepageProducts.objects.all().order_by('sequence').values('product_id')
                                         )
    product_lst = product_lst[:12]

    products = product_lst.values('id', 'title', 'retail_price',
                                  'wholesale_price', 'status__display_wholesale', 'slug')

    for product in products:
        images = []
        url = reverse('products:product-slug', kwargs={'product_slug': product['slug']})
        product_images = ProductImage.objects.filter(product__id=product['id'], image_size=1).order_by('sequence')
        for product_image in product_images:
            images.append(product_image)

        product.update({'images': images, 'url': url})

    context = {
        'products': products,
    }

    return render(request, 'index_v02.html', context)


def our_purpose(request):
    return render(request, 'our-purpose.html')


def our_purpose_retail(request):
    return render(request, 'our-purpose-retail.html')


def join_movement(request):
    if request.method == 'POST':
        form = JoinMovement(request.POST)

        if form.is_valid():
            send_join_email(form)
            return render(request, 'join-movement-complete.html')
    else:
        form = JoinMovement()

    context = {
        'join_form': form,
    }
    return render(request, 'join-movement.html', context)


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


def send_join_email(form):

    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']
    subject = form.cleaned_data['subject']
    message = form.cleaned_data['message']
    email = form.cleaned_data['email']

    email_subject = f'New Join Email {first_name} {last_name}'

    if settings.ENVIRONMENT == 'localhost':
        email_subject = f'!!TESTING!! - {subject}'

    body = f'''
        Name: {first_name} {last_name}
        Subject: {subject}
        Email: {email}
        Message:
        {message}
        '''

    html_body = f"""
                    <!DOCTYPE html>
                    <html>
                        <head>
                        </head>
                        <body>
                            <p>Name: {first_name} {last_name}</p>
                            <p>Subject: {subject}</p>
                            <p>Email: {email}</p>
                            <p>Message:</p>
                            <p>{message}</p>
                        </body>
                    </html>
                    """

    EmailThread(
        subject=email_subject,
        message=body,
        from_email=settings.EMAIL_HOST_USER,
        recipient=settings.EMAIL_HOST_USER,
        fail_silently=False,
        html_message=html_body
    ).start()

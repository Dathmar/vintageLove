from django.shortcuts import render
from products.models import Category

# Create your views here.
def index(request):
    categories = Category.objects.all()

    context = {
        'categories':  categories
    }
    return render(request, 'index.html', context)


def our_purpose(request):
    return render(request, 'our-purpose.html')


def join_movement(request):
    return render(request, 'join-movement.html')

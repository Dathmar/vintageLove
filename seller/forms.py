from django import forms
from products.models import ProductStatus, Seller, Category


class ProductForm(forms.Form):
    statuses = ProductStatus.objects.all().values_list('id', 'name')

    seller = forms.CharField(label='Seller', max_length=100, widget=forms.Select(choices=Seller.objects.all().values_list('id', 'name')))
    title = forms.CharField(label='Title', max_length=4000)
    description = forms.CharField(label='Description', max_length=8000, widget=forms.Textarea)

    dimension_width = forms.DecimalField(label='Width', max_digits=7, decimal_places=2)
    dimension_height = forms.DecimalField(label='Height', max_digits=7, decimal_places=2)
    dimension_length = forms.DecimalField(label='Length', max_digits=7, decimal_places=2)
    dimension_weight = forms.DecimalField(label='Weight', max_digits=7, decimal_places=2)

    purchase_price = forms.DecimalField(label='Purchase Price', max_digits=7, decimal_places=2)
    wholesale_price = forms.DecimalField(label='Wholesale Price', max_digits=7, decimal_places=2)
    retail_price = forms.DecimalField(label='Retail Price', max_digits=7, decimal_places=2)
    origin = forms.CharField(label='Origin', max_length=4000)

    status = forms.CharField(label='Status', max_length=100, widget=forms.Select(choices=statuses))


class ProductImageForm(forms.Form):
    image = forms.ImageField(label='Image')


class ProductCategoryForm(forms.Form):
    categories = []
    categories.append(tuple([None, 'None']))
    for cat in Category.objects.all():
        categories.append((cat.id, cat.name))

    category = forms.CharField(label='Category', max_length=100, widget=forms.Select(choices=categories))


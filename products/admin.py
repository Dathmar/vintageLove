from django.contrib import admin
from .models import Product, ProductImage, Seller, Category, ProductStatus, UserSeller


# Register your models here.
class ProductImageInline(admin.TabularInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'retail_price', 'status']
    list_filter = ['seller', 'category']
    list_editable = ['seller', 'category', 'retail_price', 'status']
    search_fields = ['title']
    exclude = ['slug']

    inlines = [
        ProductImageInline,
    ]



@admin.register(UserSeller)
class UserSellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'seller']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


admin.site.register(ProductStatus)
admin.site.register(Seller)


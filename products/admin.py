from django.contrib import admin
from .models import Product, ProductImage, Seller, Category, ProductStatus, UserSeller, ProductCategory


# Register your models here.
class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductCategoryInline(admin.TabularInline):
    model = ProductCategory


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['image', 'image_width', 'image_height']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'retail_price', 'status']
    list_filter = ['seller']
    list_editable = ['seller', 'retail_price', 'status']
    search_fields = ['title']
    exclude = ['slug']

    inlines = [
        ProductCategoryInline,
        ProductImageInline,
    ]


@admin.register(UserSeller)
class UserSellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'seller']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


admin.site.register(ProductCategory)
admin.site.register(ProductStatus)
admin.site.register(Seller)


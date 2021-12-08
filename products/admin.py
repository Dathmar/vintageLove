from django.contrib import admin
from .models import Product, ProductImage, Seller, Category, ProductStatus, UserSeller, ProductCategory, HomepageProducts


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
    list_display = ['title', 'seller', 'retail_price', 'wholesale_price', 'status']
    list_filter = ['seller']
    list_editable = ['seller', 'retail_price', 'wholesale_price', 'status']
    search_fields = ['title']
    exclude = ['slug']

    inlines = [
        ProductCategoryInline,
        ProductImageInline,
    ]


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['name', 'street', 'city', 'state', 'zip']
    list_filter = ['city', 'state']
    list_editable = ['street', 'city', 'state', 'zip']
    search_fields = ['name', 'city']


@admin.register(UserSeller)
class UserSellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'seller']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


@admin.register(HomepageProducts)
class HomepageProductsAdmin(admin.ModelAdmin):
    list_display = ['product', 'sequence']
    list_editable = ['product', 'sequence']
    list_display_links = None

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "product":
            kwargs["queryset"] = db_field.related_model.objects.filter(status__available_to_sell=True)
        return super(HomepageProductsAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(ProductCategory)
admin.site.register(ProductStatus)



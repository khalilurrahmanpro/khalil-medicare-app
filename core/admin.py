from django.contrib import admin
from .models import Medicine, Prescription, Profile, Order, Category

admin.site.register(Prescription)
admin.site.register(Order)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address',]

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'company',
        'price',
        'stock_quantity',
        'category',
    )

    search_fields = (
        'name',
        'company',
        'category__name',
    )
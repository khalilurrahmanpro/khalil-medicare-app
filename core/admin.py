from django.contrib import admin
from .models import Medicine, Prescription, Profile, Order, Category

# সাধারণ রেজিস্ট্রেশন
admin.site.register(Medicine)
admin.site.register(Prescription)
admin.site.register(Order)

# ক্যাটাগরি রেজিস্ট্রেশন
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

# প্রোফাইল রেজিস্ট্রেশন (সংশোধিত)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # এখানে phone এবং address আপনার মডেলের নামের সাথে মিল থাকতে হবে
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
from django.urls import path
from .views import update_profile , create_admin
from . import views

urlpatterns = [
    # ঔষধের তালিকা দেখার জন্য
    path('medicines/', views.get_medicines),
    
    # ইউজার রেজিস্ট্রেশন
    path('register/', views.register_user),
    
    # লগইন
    path('login/', views.login_user),
    
    # প্রোফাইল দেখার জন্য
    path('profile/', views.get_user_profile),

    path('profile/update/', update_profile),
    
    # প্রেসক্রিপশন আপলোড করার জন্য
    path('upload-prescription/', views.upload_prescription),

    path('place-order/', views.place_order), # নিশ্চিত করুন শেষে স্লাশ (/) আছে

    path('my-orders/', views.get_my_orders),
    path('categories/', views.get_categories),
    path('setup-admin/', create_admin),

] 
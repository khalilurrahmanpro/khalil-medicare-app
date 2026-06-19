from django.urls import path
from . import views

urlpatterns = [
    # --- Category & Medicine ---
    path('categories/', views.get_categories),
    path('medicines/', views.get_medicines),
    path('medicine/<int:pk>/update-stock/', views.update_stock),
    
    # --- Authentication & Profile ---
    path('register/', views.register_user),
    path('login/', views.login_user),
    path('profile/', views.get_user_profile),
    path('profile/update/', views.update_profile),
    
    # --- Prescription & Orders ---
    path('upload-prescription/', views.upload_prescription),
    path('place-order/', views.place_order), 
    path('my-orders/', views.get_my_orders),

    # --- Admin Section ---
    path('admin-orders/', views.admin_orders),
    path('admin-orders/<int:pk>/', views.update_order_status), 

    # --- App System ---
    path('check-update/', views.check_update),
]
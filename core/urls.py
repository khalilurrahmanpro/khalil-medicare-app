from django.urls import path
from .views import update_profile
from . import views

urlpatterns = [
    path('medicines/', views.get_medicines),
    
    path('register/', views.register_user),
    
    path('login/', views.login_user),
    
    path('profile/', views.get_user_profile),

    path('profile/update/', update_profile),
    
    path('upload-prescription/', views.upload_prescription),

    path('place-order/', views.place_order), 

    path('my-orders/', views.get_my_orders),

    path('categories/', views.get_categories),

    path('check-update/', views.check_update)
    
    path('admin-orders/', views.admin_orders),
]
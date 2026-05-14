from rest_framework import serializers
from .models import Medicine, Prescription, Order  
from django.contrib.auth.models import User

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'name', 'price', 'image', 'stock_quantity', 'box_discount', 'strip_discount', 'strips_per_box'] 


# এটি ব্যবহারকারীর তথ্যের জন্য (প্রোফাইল)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # এখানে অবশ্যই is_staff ফিল্ডটি থাকতে হবে
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
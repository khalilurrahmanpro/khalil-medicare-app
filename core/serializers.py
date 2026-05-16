from rest_framework import serializers
from .models import Medicine, Prescription, Order, OrderItem 
from django.contrib.auth.models import User

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='medicine.name') 
    original_price = serializers.ReadOnlyField(source='medicine.price') 
    
    class Meta:
        model = OrderItem
        fields = ['id', 'name', 'original_price', 'quantity', 'discount', 'unit']

class OrderSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    phone = serializers.ReadOnlyField(source='user.first_name') 
    
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user_username', 'phone', 'address', 'status', 
            'payment_method', 'created_at', 'total_price', 'items'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']

class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='medicine.name')
    price = serializers.ReadOnlyField(source='medicine.price') # ওষুধের একক দাম
    unit = serializers.ReadOnlyField(source='medicine.unit')   # Strip/Box
    
    class Meta:
        model = OrderItem
        fields = ['name', 'price', 'quantity', 'discount', 'unit']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True) # ওষুধের লিস্ট
    
    class Meta:
        model = Order
        fields = ['id', 'username', 'address', 'total_price', 'items', 'created_at']
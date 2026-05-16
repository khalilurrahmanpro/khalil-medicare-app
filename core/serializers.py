from rest_framework import serializers
from .models import Order, OrderItem, Medicine, Prescription
from django.contrib.auth.models import User

class OrderItemSerializer(serializers.ModelSerializer):
    medicine_name = serializers.ReadOnlyField(source='medicine.name')
    unit_price = serializers.ReadOnlyField(source='medicine.price')
    unit_type = serializers.ReadOnlyField(source='medicine.unit') # Strip/Box

    class Meta:
        model = OrderItem
        fields = ['id', 'medicine_name', 'unit_price', 'unit_type', 'quantity', 'discount']


class OrderSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username', default='Customer')
    phone = serializers.ReadOnlyField(source='user.first_name') 
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'username', 'items', 'total_price', 'address', 
            'phone', 'status', 'payment_method', 'created_at'
        ]

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
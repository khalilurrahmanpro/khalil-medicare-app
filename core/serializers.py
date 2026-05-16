from rest_framework import serializers
from .models import Order, OrderItem, Medicine

class OrderItemSerializer(serializers.ModelSerializer):
    medicine_name = serializers.ReadOnlyField(source='medicine.name')
    unit_price = serializers.ReadOnlyField(source='medicine.price')
    unit_type = serializers.ReadOnlyField(source='medicine.unit') # Strip/Box

    class Meta:
        model = OrderItem
        fields = ['id', 'medicine_name', 'unit_price', 'unit_type', 'quantity', 'discount', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'username', 'address', 'phone', 'total_price', 
            'status', 'payment_method', 'created_at', 'items'
        ]
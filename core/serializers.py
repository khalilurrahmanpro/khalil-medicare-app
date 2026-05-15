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
    username = serializers.ReadOnlyField(source='user.username')
    phone = serializers.ReadOnlyField(source='user.phone') 
    class Meta:
        model = Order
        fields = ['id', 'medicine_names', 'total_price', 'phone', 'address', 'status', 'payment_method', 'created_at']
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
        
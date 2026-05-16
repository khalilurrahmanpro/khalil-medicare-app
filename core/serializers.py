from rest_framework import serializers
from .models import Order, OrderItem, Medicine, Prescription
from django.contrib.auth.models import User

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['medicine_name', 'quantity', 'price', 'unit_type']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    medicine_summary = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'username', 'items', 'medicine_summary', 'total_price', 
            'address', 'phone', 'status', 'payment_method', 'created_at'
        ]

    def get_medicine_summary(self, obj):
        # পুরানো অর্ডারগুলোতে items না থাকলে medicine_names ফিল্ড থেকে ডাটা নিবে
        items = obj.items.all()
        if items.exists():
            return ", ".join([i.medicine_name for i in items])
        return getattr(obj, 'medicine_names', 'No Items')

# ৩. মেডিসিন সিরিয়ালাইজার
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

# ৪. প্রেসক্রিপশন সিরিয়ালাইজার
class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

# ৫. ইউজার প্রোফাইল সিরিয়ালাইজার
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']
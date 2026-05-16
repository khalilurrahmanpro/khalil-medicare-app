from rest_framework import serializers
from .models import Order, OrderItem, Medicine, Prescription
from django.contrib.auth.models import User

# ১. অর্ডার আইটেম সিরিয়ালাইজার (ইনভয়েস টেবিলের জন্য)
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        # আপনার ইনভয়েসের সব কলাম এখানে দেয়া হয়েছে
        fields = ['id', 'medicine_name', 'quantity', 'price', 'unit_type']

# ২. মেইন অর্ডার সিরিয়ালাইজার
class OrderSerializer(serializers.ModelSerializer):
    # রিলেটেড আইটেমগুলোকে লিস্ট আকারে দেখাবে
    items = OrderItemSerializer(many=True, read_only=True)
    
    # কাস্টমার ইনফরমেশন
    username = serializers.ReadOnlyField(source='user.username')
    
    # মেডিসিন সামারি (সব ওষুধের নাম একসাথে কমা দিয়ে দেখাবে)
    medicine_summary = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'username', 'items', 'medicine_summary', 'total_price', 
            'discount', 'address', 'phone', 'status', 'payment_method', 
            'transaction_id', 'created_at'
        ]

    def get_medicine_summary(self, obj):
        # এটি স্ট্রিং আকারে সব ওষুধের নাম পাঠাবে (কার্ডে দেখানোর জন্য)
        items = obj.items.all()
        if items.exists():
            return ", ".join([item.medicine_name for item in items])
        return obj.medicine_names # যদি আইটেম না থাকে তবে আগের স্ট্রিংটি দেখাবে

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
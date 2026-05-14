from rest_framework import serializers
from .models import Medicine, Prescription, Order  
from django.contrib.auth.models import User

# ১. ওষুধের জন্য সিরিয়ালাইজার (এটি ঠিক আছে)
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

# ২. প্রেসক্রিপশনের জন্য সিরিয়ালাইজার
class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

# ৩. অর্ডারের জন্য সিরিয়ালাইজার (ভুল এখানে ছিল, এটি ঠিক করুন)
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        # আপনার Order মডেলে যে ফিল্ডগুলো আছে সেগুলো এখানে দিন
        # আমি নিচের কমন ফিল্ডগুলো দিচ্ছি যা আপনার ফ্লাটার অ্যাপে ব্যবহৃত হয়েছে
        fields = ['id', 'medicine_names', 'total_price', 'address', 'status', 'payment_method', 'created_at']

# ৪. প্রোফাইলের জন্য সিরিয়ালাইজার (যাতে অ্যাডমিন চেক করা যায়)
class UserProfileSerializer(serializers.ModelSerializer):
    # যদি আপনার ইউজার মডেলে এক্সট্রা ফিল্ড (phone, address, image) থাকে
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
        # আপনার কাস্টম প্রোফাইল মডেল থাকলে নিচের মতো যোগ করুন
        # fields = ['id', 'username', 'email', 'phone', 'address', 'image', 'is_staff']
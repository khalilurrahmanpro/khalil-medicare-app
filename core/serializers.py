from rest_framework import serializers
from .models import Medicine, Prescription, Order  # এখানে Order যোগ করুন

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
        # 'id' অবশ্যই রাখবেন, তাহলে অ্যাপে #null দেখাবে না
        fields = ['id', 'medicine_names', 'total_price', 'address', 'payment_method', 'status', 'created_at']
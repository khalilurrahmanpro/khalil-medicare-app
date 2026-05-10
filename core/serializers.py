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

# --- নিচের এই অংশটুকু নতুন যোগ করুন ---
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        # এই ফিল্ডগুলোই Flutter অ্যাপে যাবে। 
        # এখানে 'id' আছে, তাই এখন আর অ্যাপে #null দেখাবে না।
        fields = [
            'id', 
            'medicine_names', 
            'total_price', 
            'address', 
            'payment_method', 
            'transaction_id', 
            'status', 
            'created_at'
        ]
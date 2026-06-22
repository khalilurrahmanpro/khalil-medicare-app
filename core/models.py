from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save 
from django.dispatch import receiver
from rest_framework import serializers
from storages.backends.s3boto3 import S3Boto3Storage


class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='medicines/',storage=S3Boto3Storage(), blank=True, null=True) 
    price_per_box = models.DecimalField(max_digits=10, decimal_places=2)
    strips_per_box = models.IntegerField(default=10) 
    box_discount_percent = models.FloatField(default=0.0)  
    strip_discount_percent = models.FloatField(default=0.0) 
    min_stock_level = models.PositiveIntegerField(default=5) 
    stock_quantity = models.PositiveIntegerField(default=0)

    @property
    def is_low_stock(self):
        return self.stock_quantity <= 2

    def __str__(self):
        return self.name


class Prescription(models.Model):
    image = models.ImageField(upload_to='prescriptions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription {self.id}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True) 
    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine_names = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    payment_method = models.CharField(max_length=20, default="COD") # COD, bKash, Nagad
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_type = models.CharField(max_length=50, default='Pcs')

    @property
    def subtotal(self):
        price = self.medicine.price
        total = price * self.quantity
        discount_amount = (total * self.discount) / 100
        return total - discount_amount

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['username', 'email', 'phone', 'address'] 

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'medicine_names', 'address', 'payment_method', 'created_at', 'phone']
        extra_kwargs = {
            'address': {'required': False, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True}
        }

    def create(self, validated_data):
        user = self.context['request'].user
        if not validated_data.get('address'):
            validated_data['address'] = user.profile.address
            
        if not validated_data.get('phone'):
            validated_data['phone'] = user.profile.phone

        return super().create(validated_data)

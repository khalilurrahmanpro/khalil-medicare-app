from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save 
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from rest_framework import serializers


class Category(models.Model):
    name = models.CharField(max_length=100)
    # আপনি চাইলে এখানে আইকন বা ছবির ফিল্ডও রাখতে পারেন
    def __str__(self):
        return self.name

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    price_per_box = models.DecimalField(max_digits=10, decimal_places=2)
    strips_per_box = models.IntegerField(default=10) 
    box_discount_percent = models.FloatField(default=0.0)  
    strip_discount_percent = models.FloatField(default=0.0) 
    min_stock_level = models.PositiveIntegerField(default=5) 
    stock_quantity = models.IntegerField(default=0)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    image = CloudinaryField('image', blank=True, null=True)

    price_per_box = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    strips_per_box = models.IntegerField(default=10)

    box_discount_percent = models.FloatField(default=0.0)

    strip_discount_percent = models.FloatField(default=0.0)

    stock_quantity = models.PositiveIntegerField(default=0)

    min_stock_level = models.PositiveIntegerField(default=5)

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
    

# models.py ফাইলে গিয়ে আপনার প্রোফাইল মডেলটি এরকম করুন:
# models.py এ গিয়ে Profile মডেলটি এমন করুন:
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    # ImageField এর বদলে CloudinaryField ব্যবহার করুন
    image = CloudinaryField('image', blank=True, null=True) 

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # শুধুমাত্র নতুন ইউজারের জন্য প্রোফাইল তৈরি করবে
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # ইউজার সেভ হলে প্রোফাইলও সেভ হবে (যদি প্রোফাইল থাকে)
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine_names = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    # নতুন পেমেন্ট ফিল্ডসমূহ
    payment_method = models.CharField(max_length=20, default="COD") # COD, bKash, Nagad
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'image']
 
# serializers.py (Django)
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        # এখানে 'id' অবশ্যই লিখবেন, নাহলে অ্যাপে #null দেখাবে
        fields = ['id', 'status', 'total_price', 'medicine_names', 'address', 'payment_method', 'created_at']
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, generics, permissions
from django.http import HttpResponse
import os

# আপনার মডেল এবং সিরিয়ালাইজার ইমপোর্ট করুন
from .models import Medicine, Prescription, Profile, Order, Category
# MedicineSerializer যদি আলাদা ফাইলে থাকে তবে সেখান থেকে ইমপোর্ট করুন, 
# নাহলে নিচে MedicineListView এর জন্য এটি লাগবে।

# ১. ক্যাটাগরি এপিআই (সবার জন্য উন্মুক্ত)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    cats = Category.objects.all().values()
    return Response(list(cats))

# ২. মেডিসিন এপিআই (সাজানো এবং ছবি সমস্যার সমাধানসহ)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_medicines(request):
    cat_id = request.GET.get('category')
    medicines = Medicine.objects.filter(category_id=cat_id) if cat_id else Medicine.objects.all()
    results = []
    
    for med in medicines:
        # Cloudinary এর ইমেজ ইউআরএল নিজেই পূর্ণাঙ্গ থাকে, তাই build_absolute_uri দরকার নেই
        image_url = med.image.url if med.image else None
        
        results.append({
            'id': med.id, 
            'name': med.name, 
            'company': med.company,
            'price': float(med.price_per_box), # নিশ্চিত করার জন্য float করা হলো
            'strips_per_box': med.strips_per_box,
            'box_discount': med.box_discount_percent,
            'strip_discount': med.strip_discount_percent,
            'description': med.description,
            'image': image_url,
        })
    return Response(results)

# ৩. ইউজার রেজিস্ট্রেশন (সংশোধিত)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    phone = request.data.get('phone')

    # চেক করা হচ্ছে ইউজারনেম বা ফোন অলরেডি আছে কি না
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    if Profile.objects.filter(phone=phone).exists():
        return Response({'error': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # ইউজার তৈরি (এটি করলে সিগন্যাল অটোমেটিক প্রোফাইল তৈরি করে দিবে)
    user = User.objects.create_user(username=username, email=email, password=password)
    
    # যেহেতু সিগন্যাল অলরেডি প্রোফাইল তৈরি করেছে, তাই আমরা শুধু ফোন নাম্বারটা আপডেট করবো
    profile = Profile.objects.get(user=user)
    profile.phone = phone
    profile.save()

    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)

# ৪. লগইন এপিআই
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    login_id = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=login_id, password=password)
    
    if not user:
        try:
            u = User.objects.get(email=login_id)
            user = authenticate(username=u.username, password=password)
        except User.DoesNotExist:
            pass

    if not user:
        try:
            p = Profile.objects.get(phone=login_id)
            user = authenticate(username=p.user.username, password=password)
        except Profile.DoesNotExist:
            pass

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# ৫. প্রোফাইল এপিআই (ভুল ঠিক করা হয়েছে)
@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_user_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    # ছবির পূর্ণাঙ্গ ইউআরএল পাওয়ার জন্য
    image_url = profile.image.url if profile.image else None
    
    return Response({
        'username': user.username,
        'email': user.email,
        'phone': profile.phone, 
        'address': profile.address,
        'image': image_url,
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    profile = user.profile # প্রোফাইল অবজেক্ট নিতে হবে

    user.email = request.data.get('email', user.email)
    profile.phone = request.data.get('phone', profile.phone)
    profile.address = request.data.get('address', profile.address)

    user.save()
    profile.save()

    return Response({"message": "Profile updated successfully"})

# ৬. প্রেসক্রিপশন আপলোড
@api_view(['POST'])
@permission_classes([AllowAny]) # প্রয়োজনে প্রটেক্টেড করতে পারেন
def upload_prescription(request):
    image = request.FILES.get('image')
    if image:
        Prescription.objects.create(image=image)
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
    return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

# ৭. অর্ডার এপিআই
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    data = request.data
    Order.objects.create(
        user=request.user,
        medicine_names=data.get('medicine_names'),
        total_price=data.get('total_price'),
        address=data.get('address'),
        payment_method=data.get('payment_method'),
        transaction_id=data.get('transaction_id')
    )
    return Response({'message': 'Order Success'}, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_orders(request):
    # ইউজারের সব অর্ডারগুলো নিচ্ছি
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    results = []
    for order in orders:
        results.append({
            'order_id': order.id,
            'medicines': order.medicine_names, # এখানে সব ঔষধের নাম থাকবে
            'total_price': float(order.total_price),
            'address': order.address,
            'status': order.status,
            'payment': order.payment_method,
            'date': order.created_at.strftime("%d %b %Y, %I:%M %p"), # তারিখটি সুন্দর দেখাবে
            'transaction_id': order.transaction_id if order.transaction_id else "N/A"
        })
    
    return Response(results)

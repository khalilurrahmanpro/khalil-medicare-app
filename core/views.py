from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status, viewsets

from .models import Medicine, Prescription, Profile, Order, Category, OrderItem
from .serializers import OrderSerializer, UserProfileSerializer

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_orders(request):
    try:
        # সব অর্ডার নিয়ে আসা
        orders = Order.objects.all().prefetch_related('items').order_by('-id')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    except Exception as e:
        # ৪‌০০ এরর কেন হচ্ছে তা দেখতে print(e) করুন
        print(f"Admin Order Error: {e}")
        return Response({"error": str(e)}, status=400)

# --- CATEGORY: ক্যাটাগরি লিস্ট ---
@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    cats = Category.objects.all().values()
    return Response(list(cats))

# --- MEDICINE: ওষুধ লিস্ট এবং সার্চ ---
@api_view(['GET'])
@permission_classes([AllowAny])
def get_medicines(request):
    cat_id = request.GET.get('category')
    medicines = Medicine.objects.filter(category_id=cat_id) if cat_id else Medicine.objects.all()
    results = []
    
    for med in medicines:
        image_url = med.image.url if med.image else None
        results.append({
            'id': med.id, 
            'name': med.name, 
            'company': med.company,
            'price': float(med.price_per_box),
            'strips_per_box': med.strips_per_box,
            'box_discount': med.box_discount_percent,
            'strip_discount': med.strip_discount_percent,
            'description': med.description,
            'image': image_url,
            'stock_quantity': med.stock_quantity,
        })
    return Response(results)

# --- AUTH: ইউজার রেজিস্ট্রেশন ---
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    if Profile.objects.filter(phone=phone).exists():
        return Response({'error': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    profile = Profile.objects.get(user=user)
    profile.phone = phone
    profile.save()

    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)

# --- AUTH: লগইন ---
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    login_id = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=login_id, password=password)
    
    if not user:
        u = User.objects.filter(email=login_id).first()
        if u: user = authenticate(username=u.username, password=password)

    if not user:
        p = Profile.objects.filter(phone=login_id).first()
        if p: user = authenticate(username=p.user.username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# --- ORDER: অর্ডার প্লেস করা (সবচেয়ে গুরুত্বপূর্ণ) ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    data = request.data
    cart_items = data.get('items') # এটি একটি লিস্ট হতে হবে
    
    try:  
        with transaction.atomic():
            # ১. মেইন অর্ডার তৈরি
            order = Order.objects.create(
                user=request.user,
                medicine_names=data.get('medicine_names'),
                total_price=data.get('total_price'),
                address=data.get('address'),
                payment_method=data.get('payment_method'),
                transaction_id=data.get('transaction_id', '') 
            )

            # ২. লুপ চালিয়ে আইটেমগুলো OrderItem টেবিলে সেভ করা
            for item in cart_items:
                medicine = Medicine.objects.get(name=item['name'])
                
                if medicine.stock_quantity < item['quantity']:
                    raise Exception(f"{medicine.name} পর্যাপ্ত স্টকে নেই!")

                # স্টক আপডেট
                medicine.stock_quantity -= item['quantity']
                medicine.save()

                # আইটেম ডাটাবেজে সেভ (এটি ইনভয়েস টেবিল ঠিক করবে)
                OrderItem.objects.create(
                    order=order,
                    medicine_name=item['name'],
                    quantity=item['quantity'],
                    price=item['price'], # নিশ্চিত করুন ফ্রন্টএন্ড থেকে price পাঠানো হচ্ছে
                )
            
            return Response({'message': 'Order Success'}, status=status.HTTP_201_CREATED)
    
    except Medicine.DoesNotExist:
        return Response({'error': 'ওষুধটি ডাটাবেজে পাওয়া যায়নি'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# --- ORDER: কাস্টমার নিজের অর্ডার দেখবে ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_orders(request):
    try:
        # prefetch_related ব্যবহার করা হয়েছে
        orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-id')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to load orders"}, status=500)

# --- ADMIN: অর্ডার স্ট্যাটাস আপডেট ---
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, pk):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=403)

    try:
        order = Order.objects.get(id=pk)
        status_value = request.data.get('status')
        if status_value:
            order.status = status_value
            order.save()
            return Response({"message": "Status Updated Successfully"})
        return Response({"error": "No status provided"}, status=400)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

# --- STOCK: স্টক আপডেট করা ---
@api_view(['PATCH', 'PUT'])
@permission_classes([AllowAny])
def update_stock(request, pk):
    try:
        medicine = Medicine.objects.get(id=pk)
        new_stock = request.data.get('stock_quantity')
        if new_stock is not None:
            medicine.stock_quantity = int(new_stock)
            medicine.save()
            return Response({"message": "Stock updated", "stock_quantity": medicine.stock_quantity})
        return Response({"error": "No stock data provided"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    # বর্তমানে যে লগইন করে আছে (request.user), তার ডাটা পাঠাবে
    user = request.user
    # প্রোফাইল মডেল থেকে ডাটা আনা (Profile মডেলটি ইমপোর্ট করা থাকতে হবে)
    profile, created = Profile.objects.get_or_create(user=user)
    
    image_url = profile.image.url if profile.image else None
    
    return Response({
        'username': user.username,
        'email': user.email,
        'phone': profile.phone, 
        'address': profile.address,
        'image': image_url,
    })

# --- PROFILE: প্রোফাইল আপডেট করার জন্য ---
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    # প্রোফাইল মডেলটি নিশ্চিত করুন (ইউজারের সাথে ওয়ান-টু-ওয়ান রিলেশন থাকতে হবে)
    profile, created = Profile.objects.get_or_create(user=user)

    user.email = request.data.get('email', user.email)
    profile.phone = request.data.get('phone', profile.phone)
    profile.address = request.data.get('address', profile.address)

    user.save()
    profile.save()

    return Response({"message": "Profile updated successfully"})

# --- STOCK: এডমিন কর্তৃক স্টক আপডেট করার জন্য ---
@api_view(['PATCH', 'PUT'])
@permission_classes([IsAdminUser])
def update_stock(request, pk):
    try:
        medicine = Medicine.objects.get(id=pk)
        new_stock = request.data.get('stock_quantity')
        
        if new_stock is not None:
            medicine.stock_quantity = int(new_stock)
            medicine.save()
            return Response({"message": "Stock updated", "stock_quantity": medicine.stock_quantity})
        return Response({"error": "No stock data provided"}, status=400)
    except Medicine.DoesNotExist:
        return Response({"error": "Medicine not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# --- PRESCRIPTION: প্রেসক্রিপশন ইমেজ আপলোড করার জন্য ---
@api_view(['POST'])
@permission_classes([AllowAny]) # প্রেসক্রিপশন যে কেউ আপলোড করতে পারবে
def upload_prescription(request):
    try:
        image = request.FILES.get('image')
        if image:
            # Prescription মডেলটি নিশ্চিত করুন আপনার models.py তে আছে
            Prescription.objects.create(image=image)
            return Response({'status': 'success', 'message': 'Prescription uploaded successfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# --- APP UPDATE: আপডেট চেক ---
@api_view(['GET'])
@permission_classes([AllowAny])
def check_update(request):
    return Response({
        "version": "1.1.0", 
        "url": "https://drive.google.com/file/d/1KwGJ2WLVFt7XG9Fsuv_texJxO7tFIbXQ/view?usp=sharing" 
    })
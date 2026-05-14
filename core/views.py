from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import OrderSerializer
from django.db import transaction
from .models import Order
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
import os
from .models import Medicine, Prescription, Profile, Order, Category
from .serializers import OrderSerializer # নিশ্চিত করুন আপনার একটি OrderSerializer আছে
from .serializers import UserSerializer 
@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    cats = Category.objects.all().values()
    return Response(list(cats))


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
            'stock_quantity': med.stock_quantity, # <--- এই লাইনটি অবশ্যই যোগ করুন
        })
    return Response(results)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    phone = request.data.get('phone')

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

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_user_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
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
    profile = user.profile 

    user.email = request.data.get('email', user.email)
    profile.phone = request.data.get('phone', profile.phone)
    profile.address = request.data.get('address', profile.address)

    user.save()
    profile.save()

    return Response({"message": "Profile updated successfully"})

@api_view(['POST'])
@permission_classes([AllowAny]) 
def upload_prescription(request):
    image = request.FILES.get('image')
    if image:
        Prescription.objects.create(image=image)
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
    return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    data = request.data
    cart_items = data.get('items') 

    try:
        with transaction.atomic():
            for item in cart_items:
                medicine = Medicine.objects.get(name=item['name'])
                
                if medicine.stock_quantity < item['quantity']:
                    return Response(
                        {'error': f"{medicine.name} পর্যাপ্ত স্টকে নেই! মাত্র {medicine.stock_quantity} টি আছে।"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                medicine.stock_quantity -= item['quantity']
                medicine.save()

            Order.objects.create(
                user=request.user,
                medicine_names=data.get('medicine_names'),
                total_price=data.get('total_price'),
                address=data.get('address'),
                payment_method=data.get('payment_method'),
                transaction_id=data.get('transaction_id', '') 
            )
            
            return Response({'message': 'Order Success'}, status=status.HTTP_201_CREATED)

    except Medicine.DoesNotExist:
        return Response({'error': 'ওষুধটি ডাটাবেজে পাওয়া যায়নি'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_orders(request):
    try:
        # বর্তমান ইউজারের সব অর্ডার নিয়ে আসা
        orders = Order.objects.filter(user=request.user).order_by('-id')
        
        # এখানে অবশ্যই সঠিক সিরিয়ালাইজার (OrderSerializer) ব্যবহার করতে হবে
        serializer = OrderSerializer(orders, many=True)
        
        return Response(serializer.data)
    except Exception as e:
        # এরর হলে কনসোলে দেখাবে কেন ৫০০ হচ্ছে
        print(f"Order Fetch Error: {e}")
        return Response({"error": "Something went wrong"}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_update(request):
    return Response({
        "version": "1.1.0", 
        "url": "https://drive.google.com/file/d/1KwGJ2WLVFt7XG9Fsuv_texJxO7tFIbXQ/view?usp=sharing" 
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_orders(request):
    orders = Order.objects.all().order_by('-id')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['PATCH', 'PUT'])
@permission_classes([AllowAny]) # আপাতত এটি AllowAny দিন যাতে টেস্ট করা যায়
def update_stock(request, pk):
    try:
        medicine = Medicine.objects.get(id=pk)
        new_stock = request.data.get('stock_quantity')
        
        if new_stock is not None:
            medicine.stock_quantity = int(new_stock) # নিশ্চিত করুন এটি নাম্বার
            medicine.save()
            return Response({"message": "Stock updated", "stock_quantity": medicine.stock_quantity}, status=200)
        return Response({"error": "No stock data provided"}, status=400)
    except Medicine.DoesNotExist:
        return Response({"error": "Medicine not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    # বর্তমানে যে লগইন করে আছে (request.user), তার ডাটা পাঠাবে
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
   

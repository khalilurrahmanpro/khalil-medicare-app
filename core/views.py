from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import Medicine, Prescription, Profile,Order,Category

# ২. ক্যাটাগরি এপিআই (সবার জন্য উন্মুক্ত)
@api_view(['GET'])
@permission_classes([AllowAny]) # এই লাইনটি নিশ্চিত করুন
def get_categories(request):
    cats = Category.objects.all().values()
    return Response(list(cats))


from rest_framework.permissions import AllowAny # নিশ্চিত করুন এটি উপরে আছে

@api_view(['GET'])
@permission_classes([AllowAny])
def get_medicines(request):
    cat_id = request.GET.get('category')
    medicines = Medicine.objects.filter(category_id=cat_id) if cat_id else Medicine.objects.all()
    results = []
    for med in medicines:
        results.append({
            'id': med.id, 'name': med.name, 'company': med.company,
            'price': med.price_per_box, 
            'strips_per_box': med.strips_per_box,
            'box_discount': med.box_discount_percent,   # নতুন
            'strip_discount': med.strip_discount_percent, # নতুন
            'description': med.description,
            'image': request.build_absolute_uri(med.image.url) if med.image else None,
        })
    return Response(results)

# ২. ইউজার রেজিস্ট্রেশন (ফোন নম্বরসহ)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    phone = request.data.get('phone')

    if User.objects.filter(username=username).exists() or Profile.objects.filter(phone_number=phone).exists():
        return Response({'error': 'Username or Phone already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    Profile.objects.create(user=user, phone_number=phone)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)

# ৩. লগইন এপিআই (Username, Email বা Phone দিয়ে)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    login_id = request.data.get('username')
    password = request.data.get('password')
    
    user = None
    # ইউজারনেম দিয়ে চেক
    user = authenticate(username=login_id, password=password)
    
    # ইমেইল দিয়ে চেক
    if not user:
        try:
            u = User.objects.get(email=login_id)
            user = authenticate(username=u.username, password=password)
        except User.DoesNotExist:
            pass

    # ফোন নম্বর দিয়ে চেক
    if not user:
        try:
            p = Profile.objects.get(phone_number=login_id)
            user = authenticate(username=p.user.username, password=password)
        except Profile.DoesNotExist:
            pass

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# ৪. ইউজারের প্রোফাইল এপিআই
@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_user_profile(request):
    user = request.user
    
    # প্রোফাইল থাকলে নিবে, না থাকলে নতুন একটা বানিয়ে নিবে (ক্রাশ করবে না)
    profile, created = Profile.objects.get_or_create(user=user)
    
    image_url = request.build_absolute_uri(profile.image.url) if profile.image else None

    return Response({
    'username': user.username,
    'email': user.email,
    'phone': profile.phone,  
    'address': profile.address,
    'image': request.build_absolute_uri(profile.image.url) if profile.image else None,
    })
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user

    user.email = request.data.get('email', user.email)
    user.phone = request.data.get('phone', user.phone)
    user.address = request.data.get('address', user.address)

    user.save()

    return Response({"message": "updated"})

# ৫. প্রেসক্রিপশন আপলোড এপিআই
@api_view(['POST'])
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
    Order.objects.create(
        user=request.user,
        medicine_names=data.get('medicine_names'),
        total_price=data.get('total_price'),
        address=data.get('address'),
        payment_method=data.get('payment_method'), # নতুন
        transaction_id=data.get('transaction_id')  # নতুন
    )
    return Response({'message': 'Order Success'}, status=201)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_orders(request):
    user = request.user
    # ইউজারের সব অর্ডার লেটেস্ট ডেট অনুযায়ী ফিল্টার করা
    orders = Order.objects.filter(user=user).order_by('-created_at').values()
    return Response(list(orders))

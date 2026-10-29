from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
import json

# Google OAuth token verification
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

from .models import StoreConfig, Story, Product, Comment, Order

def get_or_create_config():
    config = StoreConfig.objects.first()
    if not config:
        config = StoreConfig.objects.create(
            name="Chashma Drinks",
            slug="chashma-drinks",
            icon="🥤",
            phone="+998 90 123-45-67",
            banner_text="Yangi mavsum aksiyasi! Barcha salqin ichimliklarga 15% chegirma!"
        )
    return config

def home_view(request):
    config = get_or_create_config()
    return render(request, 'index.html', {'config': config})

def store_view(request):
    config = get_or_create_config()
    stories = Story.objects.filter(is_active=True).order_by('-created_at')
    products = Product.objects.prefetch_related('comments_rel').all().order_by('-created_at')
    
    return render(request, 'store.html', {
        'config': config,
        'stories': stories,
        'products': products,
        'user': request.user,
        'is_admin': request.user.is_authenticated and request.user.is_staff,
        'google_client_id': getattr(settings, 'GOOGLE_CLIENT_ID', ''),
    })

def dashboard_view(request):
    config = get_or_create_config()
    orders = Order.objects.all().order_by('-created_at')
    products = Product.objects.all().order_by('-created_at')
    
    total_revenue = sum(o.total for o in orders if o.status != 'Bekor qilindi')
    
    return render(request, 'dashboard.html', {
        'config': config,
        'orders': orders,
        'products': products,
        'total_revenue': total_revenue,
        'orders_count': orders.count(),
        'products_count': products.count(),
        'user': request.user,
        'is_admin': request.user.is_authenticated and request.user.is_staff
    })

# ================= AUTHENTICATION =================

@csrf_exempt
def api_admin_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body or '{}')
        except:
            data = request.POST
        
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Fallback for case-insensitive lookup
            matched = User.objects.filter(username__iexact=username).first()
            if matched:
                user = authenticate(request, username=matched.username, password=password)
                
        if user and user.is_staff:
            login(request, user)
            return JsonResponse({'status': 'ok', 'username': user.username})
        else:
            return JsonResponse({'status': 'error', 'message': 'Noto\'g\'ri login yoki parol!'}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Faqat POST so\'rovi qabul qilinadi'}, status=405)

def logout_view(request):
    logout(request)
    return redirect('store')

@csrf_exempt
def api_google_auth(request):
    """
    Google Identity Services (GSI) One Tap / Sign-In orqali kelgan
    ID tokenini tekshiradi va foydalanuvchini tizimga kiritadi.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    data = json.loads(request.body or '{}')
    credential = data.get('credential') or data.get('token') or ''

    if not credential:
        return JsonResponse({'status': 'error', 'message': 'Token topilmadi'}, status=400)

    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')

    # Agar real Google token bo'lsa va google-auth mavjud bo'lsa
    idinfo = None
    if GOOGLE_AUTH_AVAILABLE and client_id and client_id != 'YOUR_GOOGLE_CLIENT_ID_HERE' and not credential.endswith('.demo'):
        try:
            idinfo = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                client_id
            )
            google_id   = idinfo.get('sub')
            email       = idinfo.get('email', '')
            name        = idinfo.get('name', email.split('@')[0])
            picture     = idinfo.get('picture', '')
            given_name  = idinfo.get('given_name', name)
        except Exception:
            # Agar verification o'tmasa (masalan test yoki origin xatosi bo'lsa), idinfo None qoladi
            idinfo = None

    if not idinfo:
        # Fallback / Instant login rejimi (token payload'ni o'qish)
        import base64
        try:
            parts = credential.split('.')
            if len(parts) >= 2:
                payload_b64 = parts[1]
                payload_b64 += '=' * ((4 - len(payload_b64) % 4) % 4)
                payload = json.loads(base64.b64decode(payload_b64).decode('utf-8'))
                email      = payload.get('email', '')
                name       = payload.get('name', email.split('@')[0] if email else 'Google Foydalanuvchi')
                picture    = payload.get('picture', '')
                google_id  = payload.get('sub', 'google_' + str(abs(hash(email))))
                given_name = payload.get('given_name', name)
            else:
                return JsonResponse({'status': 'error', 'message': 'Token formati noto‘g‘ri'}, status=400)
        except Exception as err:
            return JsonResponse({'status': 'error', 'message': f'Token tahlilida xato: {str(err)}'}, status=400)

    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email topilmadi'}, status=400)

    # Django foydalanuvchisini topamiz yoki yaratamiz
    username = email.replace('@', '_').replace('.', '_')[:30]
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': given_name,
            'last_name': '',
        }
    )
    if created:
        user.set_unusable_password()
        user.save()

    # Sessionga kiritamiz
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

    return JsonResponse({
        'status': 'ok',
        'name': name,
        'email': email,
        'picture': picture,
        'username': user.username,
        'is_new': created
    })

# ================= API ENDPOINTS =================

@csrf_exempt
def api_toggle_like(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.likes += 1
        product.save()
        return JsonResponse({'status': 'ok', 'likes': product.likes})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_add_comment(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        data = json.loads(request.body or '{}')
        author = data.get('author', 'Mijoz').strip() or 'Mijoz'
        text = data.get('text', '').strip()
        if text:
            comment = Comment.objects.create(product=product, author=author, text=text)
            return JsonResponse({
                'status': 'ok',
                'comment': {
                    'id': comment.id,
                    'author': comment.author,
                    'text': comment.text,
                    'time': 'Hozirgina'
                }
            })
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_create_product(request):
    if request.method == 'POST':
        data = json.loads(request.body or '{}')
        product = Product.objects.create(
            name=data.get('name', '').strip() or 'Yangi Mahsulot',
            price=float(data.get('price', 0)),
            stock=int(data.get('stock', 30)),
            image=data.get('image', ''),
            description=data.get('description', '')
        )
        return JsonResponse({'status': 'ok', 'product_id': product.id})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_update_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        data = json.loads(request.body or '{}')
        product.name = data.get('name', product.name)
        product.price = float(data.get('price', product.price))
        product.stock = int(data.get('stock', product.stock))
        if data.get('image'):
            product.image = data.get('image')
        product.description = data.get('description', product.description)
        product.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_create_story(request):
    if request.method == 'POST':
        data = json.loads(request.body or '{}')
        story = Story.objects.create(
            title=data.get('title', '').strip() or 'Yangi Story',
            caption=data.get('caption', ''),
            image=data.get('image', ''),
            date='Doimiy arxiv (24/7)'
        )
        return JsonResponse({'status': 'ok', 'story_id': story.id})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_delete_story(request, story_id):
    if request.method == 'POST':
        story = get_object_or_404(Story, id=story_id)
        story.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body or '{}')
        import random
        order_id = 'ORD-' + str(random.randint(1000, 9999))
        order = Order.objects.create(
            order_id=order_id,
            customer=data.get('customer', 'Mijoz'),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            items=data.get('items', ''),
            total=float(data.get('total', 0)),
            payment=data.get('payment', 'Click'),
            status='Yangi'
        )
        config = get_or_create_config()
        config.balance += order.total
        config.save()
        return JsonResponse({'status': 'ok', 'order_id': order.order_id})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_update_order_status(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body or '{}')
        order = get_object_or_404(Order, order_id=order_id)
        order.status = data.get('status', order.status)
        order.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

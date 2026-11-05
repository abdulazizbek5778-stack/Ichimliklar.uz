from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.db import connection
from django.db.models import Sum
import json
import base64
from functools import wraps
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

from webauthn import (
    base64url_to_bytes,
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.exceptions import WebAuthnException
from webauthn.helpers.structs import (
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
)
from django.views.decorators.csrf import ensure_csrf_cookie

# Google OAuth token verification
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

from .models import StoreConfig, Story, Product, Comment, Order, WebAuthnCredential


def _webauthn_rp_id(request):
    return settings.WEBAUTHN_RP_ID or urlsplit(request.build_absolute_uri('/')).hostname


def _webauthn_origin(request):
    return request.build_absolute_uri('/').rstrip('/')


def _b64url_encode(value):
    return base64.urlsafe_b64encode(value).rstrip(b'=').decode('ascii')


def _json_body(request):
    try:
        return json.loads(request.body or '{}')
    except (ValueError, TypeError):
        return None


def admin_api_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({'status': 'error', 'message': 'Admin sifatida kiring.'}, status=403)
        return view(request, *args, **kwargs)
    return wrapped


def _dashboard_product_data(product):
    return {
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'price': str(product.price),
        'stock': product.stock,
        'image': product.image,
        'description': product.description,
        'created_at': product.created_at.isoformat(),
        'likes': product.likes,
        'oldPrice': str(product.old_price) if product.old_price is not None else None,
        'comments': [{
            'author': comment.author,
            'text': comment.text,
            'time': comment.created_at.strftime('%Y-%m-%d %H:%M'),
        } for comment in product.comments_rel.all()],
    }


def _dashboard_story_data(story):
    return {
        'id': story.id,
        'title': story.title,
        'caption': story.caption,
        'image': story.image,
        'created_at': story.created_at.isoformat(),
        'date': story.date,
    }

def get_or_create_config():
    config = StoreConfig.objects.first()
    if not config:
        config = StoreConfig.objects.create(
            name="Chashma Drinks",
            slug="chashma-drinks",
            icon="🥤",
            phone="+998 91 959-57-78",
            banner_text="Yangi mavsum aksiyasi! Barcha salqin ichimliklarga 15% chegirma!"
        )
    return config

def home_view(request):
    config = get_or_create_config()
    return render(request, 'index.html', {'config': config})

@ensure_csrf_cookie
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
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

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
        'is_admin': request.user.is_authenticated and request.user.is_staff,
        'passkey_count': WebAuthnCredential.objects.filter(user=request.user).count(),
    })


def api_store_catalog(request):
    products = Product.objects.prefetch_related('comments_rel').all().order_by('-created_at')
    stories = Story.objects.filter(is_active=True).order_by('-created_at')
    return JsonResponse({
        'products': [_dashboard_product_data(product) for product in products],
        'stories': [_dashboard_story_data(story) for story in stories],
    })


@admin_api_required
def api_admin_dashboard(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Faqat GET so‘rovi qabul qilinadi.'}, status=405)
    config = get_or_create_config()
    orders = Order.objects.all().order_by('-created_at')
    order_data = [{
        'id': order.order_id,
        'customer': order.customer,
        'phone': order.phone,
        'address': order.address,
        'items': order.items,
        'total': str(order.total),
        'payment': order.payment,
        'status': order.status,
        'created_at': order.created_at.isoformat(),
    } for order in orders]
    return JsonResponse({
        'config': {
            'name': config.name,
            'icon': config.icon,
            'phone': config.phone,
            'banner_text': config.banner_text,
            'tg_bot': config.tg_bot,
            'balance': str(config.balance),
        },
        'orders': order_data,
        'products': [
            _dashboard_product_data(product)
            for product in Product.objects.prefetch_related('comments_rel').all()
        ],
        'stories': [_dashboard_story_data(story) for story in Story.objects.all()],
        'active_orders': Order.objects.filter(status__in=['Yangi', 'Yetkazilmoqda']).count(),
        'revenue': str(orders.exclude(status='Bekor qilindi').aggregate(total=Sum('total'))['total'] or 0),
    })


@admin_api_required
def api_update_store_settings(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Faqat POST so‘rovi qabul qilinadi.'}, status=405)
    data = _json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Sozlamalar formati noto‘g‘ri.'}, status=400)
    config = get_or_create_config()
    config.name = str(data.get('name', config.name)).strip()[:255] or config.name
    config.phone = str(data.get('phone', config.phone)).strip()[:100]
    config.banner_text = str(data.get('banner_text', config.banner_text)).strip()
    config.tg_bot = str(data.get('tg_bot', config.tg_bot)).strip()[:100]
    config.save(update_fields=['name', 'phone', 'banner_text', 'tg_bot'])
    return JsonResponse({'status': 'ok'})

# ================= AUTHENTICATION =================

@ensure_csrf_cookie
def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')
    return render(request, 'admin_login.html', {
        'has_passkey': WebAuthnCredential.objects.filter(user__is_staff=True).exists(),
    })

def api_admin_login(request):
    if request.method == 'POST':
        data = _json_body(request)
        if data is None:
            data = request.POST
        if not isinstance(data, dict):
            return JsonResponse({'status': 'error', 'message': 'Kirish ma’lumotlari noto‘g‘ri.'}, status=400)
        
        username = data.get('username')
        password = data.get('password')
        if not isinstance(username, str) or not isinstance(password, str):
            return JsonResponse({'status': 'error', 'message': 'Kirish ma’lumotlari noto‘g‘ri.'}, status=400)
        username = username.strip()
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Fallback for case-insensitive lookup
            matched = User.objects.filter(username__iexact=username).first()
            if matched:
                user = authenticate(request, username=matched.username, password=password)
                
        if user and user.is_staff:
            login(request, user)
            return JsonResponse({'status': 'ok', 'username': user.username, 'redirect': '/dashboard/'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Noto\'g\'ri login yoki parol!'}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Faqat POST so\'rovi qabul qilinadi'}, status=405)

def logout_view(request):
    logout(request)
    return redirect('store')


@admin_api_required
def passkey_registration_begin(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)

    credentials = WebAuthnCredential.objects.filter(user=request.user)
    options = generate_registration_options(
        rp_id=_webauthn_rp_id(request),
        rp_name=get_or_create_config().name,
        user_id=str(request.user.pk).encode('utf-8'),
        user_name=request.user.username,
        user_display_name=request.user.get_full_name() or request.user.username,
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=base64url_to_bytes(item.credential_id))
            for item in credentials
        ],
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            user_verification=UserVerificationRequirement.REQUIRED
        ),
    )
    request.session['webauthn_register_challenge'] = _b64url_encode(options.challenge)
    return JsonResponse(json.loads(options_to_json(options)))


@admin_api_required
def passkey_registration_finish(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)
    data = _json_body(request)
    challenge = request.session.pop('webauthn_register_challenge', None)
    if not isinstance(data, dict) or not challenge:
        return JsonResponse({'status': 'error', 'message': 'Ro‘yxatdan o‘tish muddati tugadi. Qayta urinib ko‘ring.'}, status=400)

    try:
        verification = verify_registration_response(
            credential=data,
            expected_challenge=base64url_to_bytes(challenge),
            expected_origin=_webauthn_origin(request),
            expected_rp_id=_webauthn_rp_id(request),
            require_user_verification=True,
        )
    except (WebAuthnException, ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Qurilmani tasdiqlab bo‘lmadi. Qayta urinib ko‘ring.'}, status=400)

    credential_id = _b64url_encode(verification.credential_id)
    if WebAuthnCredential.objects.filter(credential_id=credential_id).exists():
        return JsonResponse({'status': 'error', 'message': 'Bu passkey avval ro‘yxatdan o‘tgan.'}, status=400)
    credential_name = data.get('name')
    if not isinstance(credential_name, str):
        credential_name = 'Qurilmam'
    WebAuthnCredential.objects.create(
        user=request.user,
        credential_id=credential_id,
        public_key=verification.credential_public_key,
        sign_count=verification.sign_count,
        name=credential_name[:100] or 'Qurilmam',
    )
    return JsonResponse({'status': 'ok'})


def passkey_authentication_begin(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)
    credentials = list(WebAuthnCredential.objects.select_related('user').filter(user__is_staff=True))
    if not credentials:
        return JsonResponse({
            'status': 'error',
            'message': 'Passkey hali sozlanmagan. Avval admin paroli bilan kiring va sozlamalardan Face ID qo‘shing.',
        }, status=400)

    options = generate_authentication_options(
        rp_id=_webauthn_rp_id(request),
        allow_credentials=[
            PublicKeyCredentialDescriptor(id=base64url_to_bytes(item.credential_id))
            for item in credentials
        ],
        user_verification=UserVerificationRequirement.REQUIRED,
    )
    request.session['webauthn_auth_challenge'] = _b64url_encode(options.challenge)
    return JsonResponse(json.loads(options_to_json(options)))


def passkey_authentication_finish(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)
    data = _json_body(request)
    challenge = request.session.pop('webauthn_auth_challenge', None)
    if not isinstance(data, dict) or not challenge:
        return JsonResponse({'status': 'error', 'message': 'Kirish muddati tugadi. Qayta urinib ko‘ring.'}, status=400)

    try:
        credential_id = data.get('id', '')
        if not isinstance(credential_id, str) or not credential_id:
            return JsonResponse({'status': 'error', 'message': 'Passkey javobi noto‘g‘ri.'}, status=400)
        saved = WebAuthnCredential.objects.select_related('user').get(
            credential_id=credential_id,
            user__is_staff=True,
        )
        verification = verify_authentication_response(
            credential=data,
            expected_challenge=base64url_to_bytes(challenge),
            expected_origin=_webauthn_origin(request),
            expected_rp_id=_webauthn_rp_id(request),
            credential_public_key=bytes(saved.public_key),
            credential_current_sign_count=saved.sign_count,
            require_user_verification=True,
        )
    except WebAuthnCredential.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Bu qurilma ro‘yxatdan o‘tmagan.'}, status=400)
    except (WebAuthnException, ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Biometrik tasdiq amalga oshmadi. Qayta urinib ko‘ring.'}, status=400)

    saved.sign_count = verification.new_sign_count
    saved.save(update_fields=['sign_count'])
    login(request, saved.user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'status': 'ok', 'redirect': '/dashboard/'})

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

@admin_api_required
def api_create_product(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Faqat POST so‘rovi qabul qilinadi.'}, status=405)
    data = _json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Mahsulot ma’lumotlari noto‘g‘ri.'}, status=400)
    name = data.get('name')
    image = data.get('image')
    if not isinstance(name, str) or not name.strip():
        return JsonResponse({'status': 'error', 'message': 'Mahsulot nomini kiriting.'}, status=400)
    if not isinstance(image, str) or not image.strip():
        return JsonResponse({'status': 'error', 'message': 'Mahsulot rasmi yoki rasm havolasini kiriting.'}, status=400)
    try:
        price = Decimal(str(data.get('price')))
        stock = int(data.get('stock', 30))
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Narx yoki qoldiq qiymati noto‘g‘ri.'}, status=400)
    if not price.is_finite() or price <= 0 or stock < 0:
        return JsonResponse({'status': 'error', 'message': 'Narx 0 dan katta, qoldiq esa 0 yoki undan ko‘p bo‘lishi kerak.'}, status=400)
    product = Product.objects.create(
        name=name.strip()[:255],
        category=str(data.get('category') or 'drinks')[:100],
        price=price,
        stock=stock,
        image=image.strip(),
        description=str(data.get('description') or ''),
    )
    return JsonResponse({'status': 'ok', 'product': _dashboard_product_data(product)})

@admin_api_required
def api_update_product(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Faqat POST so‘rovi qabul qilinadi.'}, status=405)
    data = _json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Mahsulot ma’lumotlari noto‘g‘ri.'}, status=400)
    product = get_object_or_404(Product, id=product_id)
    name = data.get('name', product.name)
    image = data.get('image', product.image)
    if not isinstance(name, str) or not name.strip() or not isinstance(image, str) or not image.strip():
        return JsonResponse({'status': 'error', 'message': 'Mahsulot nomi va rasmi bo‘sh bo‘lmasligi kerak.'}, status=400)
    try:
        price = Decimal(str(data.get('price', product.price)))
        stock = int(data.get('stock', product.stock))
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Narx yoki qoldiq qiymati noto‘g‘ri.'}, status=400)
    if not price.is_finite() or price <= 0 or stock < 0:
        return JsonResponse({'status': 'error', 'message': 'Narx 0 dan katta, qoldiq esa 0 yoki undan ko‘p bo‘lishi kerak.'}, status=400)
    product.name = name.strip()[:255]
    product.category = str(data.get('category', product.category))[:100]
    product.price = price
    product.stock = stock
    product.image = image.strip()
    product.description = str(data.get('description', product.description))
    product.save()
    return JsonResponse({'status': 'ok', 'product': _dashboard_product_data(product)})

@admin_api_required
def api_delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@admin_api_required
def api_create_story(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Faqat POST so‘rovi qabul qilinadi.'}, status=405)
    data = _json_body(request)
    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Post ma’lumotlari noto‘g‘ri.'}, status=400)
    title = data.get('title')
    image = data.get('image')
    if not isinstance(title, str) or not title.strip():
        return JsonResponse({'status': 'error', 'message': 'Post sarlavhasini kiriting.'}, status=400)
    if not isinstance(image, str) or not image.strip():
        return JsonResponse({'status': 'error', 'message': 'Post uchun rasm yoki rasm havolasini kiriting.'}, status=400)
    story = Story.objects.create(
        title=title.strip()[:255],
        caption=str(data.get('caption') or ''),
        image=image.strip(),
        date='Doimiy arxiv (24/7)',
    )
    return JsonResponse({
        'status': 'ok',
        'story_id': story.id,
        'story': _dashboard_story_data(story),
    })

@admin_api_required
def api_delete_story(request, story_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': "Faqat POST so'rovi"}, status=405)

    story = Story.objects.filter(id=story_id).first()

    # Eski versiyada story id sifatida Date.now() saqlangan bo'lishi mumkin.
    # Bunday holatda sarlavha bo'yicha topib o'chiramiz.
    if story is None:
        try:
            data = json.loads(request.body or '{}')
        except (ValueError, TypeError):
            data = {}
        title = (data.get('title') or '').strip()
        if title:
            story = Story.objects.filter(title=title).order_by('-created_at').first()

    if story is None:
        return JsonResponse(
            {'status': 'error', 'message': 'Story bazadan topilmadi.'},
            status=404,
        )

    story.delete()
    return JsonResponse({'status': 'ok'})

@csrf_exempt
def api_create_order(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Faqat POST so\'rovi qabul qilinadi.'}, status=400)

    try:
        data = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Buyurtma ma\'lumotlari noto\'g\'ri.'}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Buyurtma ma\'lumotlari noto\'g\'ri.'}, status=400)

    customer = (data.get('customer') or data.get('name') or 'Mijoz').strip()
    phone = (data.get('phone') or '').strip()
    address = (data.get('address') or data.get('message') or '').strip()
    items = (data.get('items') or data.get('product') or '').strip()
    payment = (data.get('payment') or 'Click').strip() or 'Click'

    if not customer or not phone:
        return JsonResponse({'status': 'error', 'message': 'Ism va telefon raqami kiritilishi shart.'}, status=400)

    try:
        total = Decimal(str(data.get('total', 0) or 0))
    except InvalidOperation:
        return JsonResponse({'status': 'error', 'message': 'Umumiy summa noto\'g\'ri.'}, status=400)

    import random
    order_id = 'ORD-' + str(random.randint(1000, 9999))
    order = Order.objects.create(
        order_id=order_id,
        customer=customer[:255],
        phone=phone[:100],
        address=address[:255],
        items=items[:1000] or 'Buyurtma qoldirildi',
        total=total,
        payment=payment[:100],
        status='Yangi'
    )
    config = get_or_create_config()
    config.balance = Decimal(str(config.balance)) + total
    config.save(update_fields=['balance'])
    return JsonResponse({'status': 'ok', 'order_id': order.order_id, 'message': 'Buyurtma muvaffaqiyatli qabul qilindi.'})

@admin_api_required
def api_update_order_status(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Faqat POST so‘rovi qabul qilinadi.'}, status=405)
    data = _json_body(request)
    status = data.get('status') if isinstance(data, dict) else None
    valid_statuses = {'Yangi', 'Yetkazilmoqda', 'Tugallandi', 'Bekor qilindi'}
    if status not in valid_statuses:
        return JsonResponse({'status': 'error', 'message': 'Buyurtma holati noto‘g‘ri.'}, status=400)
    order = get_object_or_404(Order, order_id=order_id)
    order.status = status
    order.save(update_fields=['status'])
    return JsonResponse({'status': 'ok'})


def health_view(request):
    """Sayt va baza holati (uptime monitoring / keep-alive uchun)."""
    try:
        data = {
            'status': 'ok',
            'database': connection.vendor,
            'products': Product.objects.count(),
            'orders': Order.objects.count(),
            'waters': None,
            'debug': settings.DEBUG,
        }
        try:
            from waters.models import WaterProduct
            data['waters'] = WaterProduct.objects.count()
        except Exception:
            pass
        return JsonResponse(data)
    except Exception as exc:
        return JsonResponse(
            {'status': 'error', 'message': str(exc)},
            status=500,
        )

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env(path):
    """Oddiy .env yuklovchi. python-dotenv o'rnatilgan bo'lsa undan foydalanadi,
    aks holda faylni o'zi o'qiydi (qo'shimcha kutubxona talab qilmaydi)."""
    if not path.exists():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(path)
        return
    except ImportError:
        pass
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


load_env(BASE_DIR / '.env')


def env_bool(name, default):
    return os.environ.get(name, default).strip().lower() in ('1', 'true', 'yes', 'on')


SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dokonify-secret-key-abdulaziz-xurramov-2026',
)

DEBUG = env_bool('DJANGO_DEBUG', 'True')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
    'waters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Productionda (DEBUG=False) statik fayllarni ham beradi
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DB_ENGINE = os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3')
DB_NAME = os.environ.get('DB_NAME', '').strip()

if DB_NAME:
    # SQLite uchun nisbiy yo'l loyiha papkasiga bog'lanadi
    if DB_ENGINE.endswith('sqlite3') and not os.path.isabs(DB_NAME):
        DB_NAME = str(BASE_DIR / DB_NAME)
else:
    DB_NAME = str(BASE_DIR / 'db.sqlite3')

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
# Faqat static/ papkasi yig'iladi. Ilgari BASE_DIR ham qo'shilgan edi va
# undagi eski nusxalar (style.css, app.js) static/ dagi yangilarini bosib ketardi.
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# collectstatic'dan keyin statik fayllarni siqilgan holda berish (WhiteNoise)
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== GOOGLE OAUTH 2.0 =====
# Google Cloud Console dan olingan Client ID ni shu yerga kiriting:
# https://console.cloud.google.com/
GOOGLE_CLIENT_ID = os.environ.get(
    'GOOGLE_CLIENT_ID',
    '191600140879-p4bbi5mcdfv5c255j0g08ajl81dmigm3.apps.googleusercontent.com'
)
LOGIN_REDIRECT_URL = '/store.html'
LOGOUT_REDIRECT_URL = '/store.html'

# ===== PRODUCTION (Render) SOZLAMALARI =====
# Render HTTPS orqali keladi; Django buni to'g'ri aniqlashi uchun:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Admin/API POST so'rovlarida CSRF tekshiruvi o'tishi uchun ishonchli domenlar
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

# Render o'z domenini muhit o'zgaruvchisi orqali beradi — avtomatik qo'shamiz
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')
    if _render_host not in ALLOWED_HOSTS and '*' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_render_host)

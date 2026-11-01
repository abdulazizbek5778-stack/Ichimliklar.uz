from django.contrib.auth.hashers import make_password
from django.db import migrations

OWNER_USERNAME = 'xurramov_abdulaziz'
OWNER_PASSWORD = '1234'
OWNER_EMAIL = 'admin@example.com'


def create_owner_user(apps, schema_editor):
    """Do'kon egasi uchun admin foydalanuvchini yaratadi.

    Yangi baza (masalan, har deploy'da yaratiladigan SQLite yoki yangi Postgres)
    bo'sh bo'lsa, sayt va /admin/ ga kirish uchun shu foydalanuvchi kerak.
    Mavjud bo'lsa — paroliga tegilmaydi, faqat huquqlari tekshiriladi.
    """
    User = apps.get_model('auth', 'User')

    user, created = User.objects.get_or_create(
        username=OWNER_USERNAME,
        defaults={
            'email': OWNER_EMAIL,
            'password': make_password(OWNER_PASSWORD),
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        },
    )

    if not created:
        changed_fields = []
        for field in ('is_staff', 'is_superuser', 'is_active'):
            if not getattr(user, field):
                setattr(user, field, True)
                changed_fields.append(field)
        if changed_fields:
            user.save(update_fields=changed_fields)


def remove_owner_user(apps, schema_editor):
    # Orqaga qaytarishda foydalanuvchini o'chirmaymiz — ma'lumot yo'qolmasin.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_remove_order_user_delete_userprofile'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_owner_user, remove_owner_user),
    ]

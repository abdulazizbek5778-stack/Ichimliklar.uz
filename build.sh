#!/usr/bin/env bash
# =======================================
# Render build skripti
# Render Dashboard -> Settings -> Build Command:  ./build.sh
# =======================================
set -o errexit

echo "📦 Kutubxonalar o'rnatilmoqda..."
pip install -r requirements.txt

echo "🎨 Statik fayllar yig'ilmoqda..."
python manage.py collectstatic --noinput

echo "🗄️  Migratsiyalar qo'llanilmoqda..."
python manage.py migrate --noinput

echo "👤 Admin foydalanuvchi tekshirilmoqda..."
python manage.py ensure_superuser

echo "🌱 Bo'sh baza bo'lsa, boshlang'ich ma'lumotlar yuklanadi..."
python manage.py seed_if_empty

echo "✅ Build tugadi."

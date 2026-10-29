#!/bin/bash
# =======================================
# ichimliklar.uz — Django Ishga Tushirish
# =======================================

echo ""
echo "🚀 ichimliklar.uz Django serveri ishga tushmoqda..."
echo ""

# 1. Port 8000 ni tozalash
PID=$(lsof -ti :8000 2>/dev/null)
if [ -n "$PID" ]; then
  echo "⚠️  Port 8000 band edi, o'chirildi (PID: $PID)"
  kill -9 $PID 2>/dev/null
  sleep 1
fi

# 2. Papkaga o'tish
cd "$(dirname "$0")"

# 3. Migratsiyalar (yangi modellar bo'lsa)
echo "📦 Migratsiyalar tekshirilmoqda..."
python3 manage.py makemigrations shop 2>/dev/null
python3 manage.py migrate 2>/dev/null

# 4. Serverni ishga tushirish
echo ""
echo "✅ Server muvaffaqiyatli ishga tushdi!"
echo ""
echo "   🌐 Sayt:         http://localhost:8000/store.html"
echo "   📊 Dashboard:    http://localhost:8000/dashboard/"
echo "   ⚙️  Django Admin: http://localhost:8000/admin/"
echo ""
echo "   🔑 Login: xurramov_abdulaziz"
echo "   🔑 Parol: 1234"
echo ""
echo "   Serverdan chiqish uchun: Ctrl+C"
echo ""

python3 manage.py runserver 127.0.0.1:8000

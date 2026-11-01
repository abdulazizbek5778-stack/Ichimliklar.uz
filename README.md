# 🛍️ Dokonify.uz — Web & Telegram Do'kon Yaratish Platformasi (SaaS)

Kichik va o'rta bizneslar, ichimliklar do'konlari, brendlar va kafelar uchun 3 daqiqada zamonaviy Web-sayt va Telegram WebApp do'kon yaratib beruvchi avtomatlashtirilgan savdo platformasi.

---

## 🌟 Loyiha Nimalarni O'z Ichiga Oladi?

1. **Bosh Sahifa & Do'kon Konstruktori (`index.html`):**
   - Zamonaviy ultra-premium Landing Page (Stripe / Apple darajasidagi dizayn)
   - Jonli Interaktiv Do'kon Yaratish (Wizard) — do'kon nomini kiritganda yonidagi telefon ekranida darhol o'zgaradi
   - Kategoriya tanlash: Ichimliklar (Drinks), Kiyim-kechak (Fashion), Fast Food, Gadjetlar
   - Tariflar va xizmatlar taqdimoti (SaaS monetizatsiyasi)

2. **Xaridorlar uchun Do'kon Vitrinasi (`store.html`):**
   - Mahsulotlar katalogi, aksiyalar va chegirma belgilari
   - Qidiruv va filtrlash
   - Savatcha (Cart Drawer)
   - Click, Payme va Naqd pul orqali buyurtma berish
   - **Telegram WebApp** rejimida sinab ko'rish imkoniyati (bir tugma bilan Telegram mini-app ko'rinishiga o'tadi)
   - Buyurtma qabul qilinganda elektron chek chiqarish

3. **Do'kon Egasining Boshqaruv Paneli (`dashboard.html`):**
   - Real-time savdo statistikasi va tushumlar hisoblagichi
   - Buyurtmalar boshqaruvi (Yangi -> Yetkazilmoqda -> Tugallandi -> Bekor qilindi)
   - Mahsulot qo'shish va o'chirish
   - Telegram Bot va Click/Payme to'lov sozlamalari
   - Do'kon nomini va bannerlarini tahrirlash

---

## 🚀 Ishga Tushirish

Loyihani istalgan kompyuterda yoki serverda ishga tushirish uchun:

```bash
# Python dev server orqali:
python3 -m http.server 8000
```

Brauzerda ochish:
- **Asosiy platforma:** http://localhost:8000/
- **Do'kon vitrinasi (Mijozlar ko'radigan sayt):** http://localhost:8000/store.html
- **Admin Boshqaruv paneli:** http://localhost:8000/dashboard.html

---

## 💰 Qanday qilib bu loyihani sotish va daromad qilish mumkin?

1. **Obuna (SaaS) modeli:** Do'kon egalariga oyiga 149,000 so'm evaziga tayyor Web + Telegram do'kon berish. 100 ta do'kon = oyiga 14,900,000 so'm sof daromad.
2. **Bir martalik sotish (Tayyor loyiha):** Ichimlik do'konlari, suv yetkazib beruvchilar yoki butiklarga ushbu platformani shaxsiy brendi bilan $300 - $1,500 ga tayyor qilib o'rnatib berish mumkin.
3. **To'lov komissiyasi:** Click va Payme orqali har bir buyurtmadan 0.5% - 1% tranzaksiya haqi olish.

Yaratuvchi: **Xurramov Abdulaziz**

---

## 🌐 Render'da doimiy ishlash (PostgreSQL)

Render'ning vaqtinchalik diski har deploy'da o'chib ketadi, shuning uchun SQLite o'rniga
**PostgreSQL** ishlatiladi. Kod `DATABASE_URL` muhit o'zgaruvchisini avtomatik o'qiydi
(`core/settings.py`). `DATABASE_URL` bo'lmasa lokal SQLite ishlayveradi.

### 1. Baza yaratish

Render Dashboard → **New +** → **Postgres** → nomi: `ichimliklar-db` → rejani tanlang → **Create**.
Yaratilgach **Connections** bo'limidan **Internal Database URL** ni nusxalang
(`postgresql://...` ko'rinishida).

### 2. Web servisga ulash

Render Dashboard → saytingiz servisi → **Environment** → **Add Environment Variable**:

| Key | Value |
|---|---|
| `DATABASE_URL` | nusxalangan **Internal Database URL** |
| `DJANGO_SUPERUSER_USERNAME` | `admin` (o'zingiz xohlagan login) |
| `DJANGO_SUPERUSER_EMAIL` | `admin@example.com` |
| `DJANGO_SUPERUSER_PASSWORD` | kuchli parol |
| `DJANGO_DEBUG` | `False` |

So'ng **Manual Deploy → Deploy latest commit**.

### 3. Build Command (bir marta o'zgartiriladi)

Servis → **Settings** → **Build Command**:

```bash
./build.sh
```

`build.sh` kutubxonalarni o'rnatadi, statik fayllarni yig'adi, migratsiyalarni qo'llaydi,
adminni yaratadi va baza bo'sh bo'lsa boshlang'ich mahsulotlarni yuklaydi.

### 4. Ma'lumotlar saqlanadimi?

Ha. Endi mahsulotlar, buyurtmalar va admin parol har deploy'dan keyin ham saqlanadi.

> Eslatma: Render bepul PostgreSQL ba'zi tariflarda muddatli bo'ladi. Butunlay bepul va
> doimiy baza kerak bo'lsa **Neon.tech** yoki **Supabase** ishlatsa bo'ladi — ular ham
> `DATABASE_URL` beradi, qolgan sozlash bir xil.

### 5. Sayt uxlab qolmasligi (keep-alive)

`.github/workflows/keepalive.yml` har 10 daqiqada saytga so'rov yuboradi, shunda Render
bepul rejasidagi servis uxlab qolmaydi. GitHub'da **Actions** bo'limi yoqilgan bo'lishi kerak.


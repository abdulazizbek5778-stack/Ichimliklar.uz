from django.db import models
from django.utils import timezone

class StoreConfig(models.Model):
    name = models.CharField(max_length=255, default="Chashma Drinks", verbose_name="Do'kon nomi")
    slug = models.SlugField(default="chashma-drinks", verbose_name="Slug")
    icon = models.CharField(max_length=50, default="🥤", verbose_name="Belgi (Icon)")
    phone = models.CharField(max_length=100, default="+998 90 123-45-67", verbose_name="Telefon")
    address = models.CharField(max_length=255, default="Toshkent shahri, Chilonzor tumani", verbose_name="Manzil")
    banner_text = models.TextField(default="Yangi mavsum aksiyasi! Barcha salqin ichimliklarga 15% chegirma!", verbose_name="Aksiya banner matni")
    tg_bot = models.CharField(max_length=100, default="@chashma_drinks_bot", verbose_name="Telegram Bot")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=3840000, verbose_name="Balans (so'm)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Do'kon Sozlamasi"
        verbose_name_plural = "Do'kon Sozlamalari"


class Story(models.Model):
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    caption = models.TextField(blank=True, verbose_name="Tavsif / Matn")
    image = models.TextField(verbose_name="Rasm (URL yoki Base64)")
    date = models.CharField(max_length=100, default="Doimiy arxiv (24/7)", verbose_name="Vaqt / Holat")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories (24/7 Arxiv)"
        ordering = ['-created_at']


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Mahsulot nomi")
    category = models.CharField(max_length=100, default="drinks", verbose_name="Kategoriya")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narxi (so'm)")
    old_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Eski narxi")
    image = models.TextField(verbose_name="Rasm (URL yoki Base64)")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    stock = models.IntegerField(default=30, verbose_name="Qoldiq (dona)")
    is_popular = models.BooleanField(default=True, verbose_name="Ommabopmi?")
    likes = models.IntegerField(default=0, verbose_name="Layklar soni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    def __str__(self):
        return self.name

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-created_at']


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments_rel', verbose_name="Mahsulot")
    author = models.CharField(max_length=150, default="Mijoz", verbose_name="Muallif")
    text = models.TextField(verbose_name="Izoh matni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yozilgan vaqti")

    def __str__(self):
        return f"{self.author} - {self.product.name}"

    class Meta:
        verbose_name = "Izoh / Sharh"
        verbose_name_plural = "Izohlar va Sharhlar"
        ordering = ['-created_at']


class Order(models.Model):
    order_id = models.CharField(max_length=50, unique=True, verbose_name="Buyurtma ID")
    customer = models.CharField(max_length=255, verbose_name="Xaridor ismi")
    phone = models.CharField(max_length=100, verbose_name="Telefon raqami")
    address = models.CharField(max_length=255, verbose_name="Yetkazish manzili")
    items = models.TextField(verbose_name="Mahsulotlar")
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Jami summa (so'm)")
    payment = models.CharField(max_length=100, default="Click", verbose_name="To'lov turi")
    status = models.CharField(max_length=100, default="Yangi", verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sana")

    def __str__(self):
        return f"{self.order_id} - {self.customer}"

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']

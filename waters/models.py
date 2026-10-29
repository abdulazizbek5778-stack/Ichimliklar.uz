from django.db import models

class WaterProduct(models.Model):
    WATER_TYPES = (
        ('sparkling', 'Gazlangan Mineral Suv'),
        ('still', 'Gazsiz Toza Buloq Suvi (Bezgaz)'),
    )

    name = models.CharField(max_length=255, verbose_name="Suv nomi")
    water_type = models.CharField(max_length=50, choices=WATER_TYPES, default='still', verbose_name="Suv turi")
    volume = models.CharField(max_length=50, default="0.5L", verbose_name="Hajmi (litr)")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narxi (so'm)")
    old_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Eski narxi (so'm)")
    stock = models.IntegerField(default=50, verbose_name="Ombordagi qoldiq (dona)")
    origin = models.CharField(max_length=255, verbose_name="Kelib chiqishi / Manbasi")
    mineralization = models.CharField(max_length=255, blank=True, verbose_name="Minerallashuv darajasi")
    ph_level = models.CharField(max_length=50, default="7.2 pH", verbose_name="pH ko'rsatkichi")
    image = models.TextField(verbose_name="Rasm (URL yoki Base64)")
    description = models.TextField(verbose_name="Tavsif")
    benefits = models.TextField(blank=True, verbose_name="Foydali xususiyatlari")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqti")

    def __str__(self):
        return f"{self.name} ({self.stock} dona)"

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    class Meta:
        verbose_name = "Suv Mahsuloti"
        verbose_name_plural = "Suv Mahsulotlari (Borjomi & Gazsiz)"
        ordering = ['id']

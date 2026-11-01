from django.core.management import call_command
from django.core.management.base import BaseCommand

from shop.models import Product
from waters.models import WaterProduct


class Command(BaseCommand):
    help = "Baza bo'sh bo'lsa, boshlang'ich do'kon ma'lumotlarini (mahsulotlar, suvlar) yuklaydi."

    def handle(self, *args, **options):
        if Product.objects.exists() or WaterProduct.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Bazada ma'lumot bor — seed o'tkazib yuborildi."
            ))
            return

        call_command('loaddata', 'seed_data.json', verbosity=0)
        self.stdout.write(self.style.SUCCESS(
            f"Boshlang'ich ma'lumot yuklandi: "
            f"{Product.objects.count()} mahsulot, "
            f"{WaterProduct.objects.count()} suv."
        ))

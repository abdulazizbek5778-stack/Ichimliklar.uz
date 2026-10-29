from django.shortcuts import render
from django.http import JsonResponse
from .models import WaterProduct
from shop.models import StoreConfig

def waters_showcase_view(request):
    """
    Maxsus Suvlar Bo'limi (Borjomi va Gazsiz / Bezgaz mineral suvlar)
    """
    config = StoreConfig.objects.first()
    waters = WaterProduct.objects.filter(is_active=True).order_by('id')
    return render(request, 'waters.html', {
        'config': config,
        'waters': waters,
        'user': request.user,
    })

def api_water_list(request):
    waters = WaterProduct.objects.filter(is_active=True).values(
        'id', 'name', 'water_type', 'volume', 'price', 'old_price',
        'stock', 'origin', 'mineralization', 'ph_level', 'image',
        'description', 'benefits'
    )
    return JsonResponse({'status': 'ok', 'waters': list(waters)})

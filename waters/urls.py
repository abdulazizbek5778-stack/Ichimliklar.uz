from django.urls import path
from . import views

app_name = 'waters'

urlpatterns = [
    path('', views.waters_showcase_view, name='showcase'),
    path('api/list/', views.api_water_list, name='api_list'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('store/', views.store_view, name='store'),
    path('store.html', views.store_view, name='store_html'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard.html', views.dashboard_view, name='dashboard_html'),
    path('index.html', views.home_view, name='index_html'),
    
    # Auth
    path('api/auth/login/', views.api_admin_login, name='api_admin_login'),
    path('api/auth/google/', views.api_google_auth, name='api_google_auth'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints
    path('api/like/<int:product_id>/', views.api_toggle_like, name='api_like'),
    path('api/comment/<int:product_id>/', views.api_add_comment, name='api_comment'),
    path('api/product/create/', views.api_create_product, name='api_product_create'),
    path('api/product/update/<int:product_id>/', views.api_update_product, name='api_product_update'),
    path('api/product/delete/<int:product_id>/', views.api_delete_product, name='api_product_delete'),
    path('api/story/create/', views.api_create_story, name='api_story_create'),
    path('api/story/delete/<int:story_id>/', views.api_delete_story, name='api_story_delete'),
    path('api/order/create/', views.api_create_order, name='api_order_create'),
    path('api/order/status/<str:order_id>/', views.api_update_order_status, name='api_order_status'),
]

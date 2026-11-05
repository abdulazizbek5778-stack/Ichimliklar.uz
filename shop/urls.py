from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('store/', views.store_view, name='store'),
    path('store.html', views.store_view, name='store_html'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard.html', views.dashboard_view, name='dashboard_html'),
    path('index.html', views.home_view, name='index_html'),
    path('owner/login/', views.admin_login_view, name='admin_login'),

    # Monitoring / keep-alive
    path('healthz/', views.health_view, name='health'),
    
    # Auth
    path('api/auth/login/', views.api_admin_login, name='api_admin_login'),
    path('api/auth/google/', views.api_google_auth, name='api_google_auth'),
    path('api/auth/passkey/register/begin/', views.passkey_registration_begin, name='passkey_registration_begin'),
    path('api/auth/passkey/register/finish/', views.passkey_registration_finish, name='passkey_registration_finish'),
    path('api/auth/passkey/login/begin/', views.passkey_authentication_begin, name='passkey_authentication_begin'),
    path('api/auth/passkey/login/finish/', views.passkey_authentication_finish, name='passkey_authentication_finish'),
    path('api/store/catalog/', views.api_store_catalog, name='api_store_catalog'),
    path('api/admin/dashboard/', views.api_admin_dashboard, name='api_admin_dashboard'),
    path('api/admin/settings/', views.api_update_store_settings, name='api_update_store_settings'),
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

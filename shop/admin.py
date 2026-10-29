from django.contrib import admin
from .models import StoreConfig, Story, Product, Comment, Order

@admin.register(StoreConfig)
class StoreConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'balance', 'tg_bot')

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'caption')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'likes', 'created_at')
    list_filter = ('category', 'is_popular', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'created_at')
    search_fields = ('author', 'text', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'phone', 'total', 'payment', 'status', 'created_at')
    list_filter = ('status', 'payment', 'created_at')
    search_fields = ('order_id', 'customer', 'phone', 'address')

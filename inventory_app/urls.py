from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Stock Management URLs
    path('products/<int:pk>/stock_in/', views.stock_in, name='stock_in'),
    path('products/<int:pk>/stock_out/', views.stock_out, name='stock_out'),

    # Stock In/Out by Barcode
    path('stock_in_by_barcode/', views.stock_in_by_barcode, name='stock_in_by_barcode'),
    path('stock_out_by_barcode/', views.stock_out_by_barcode, name='stock_out_by_barcode'),

    # Stock Movements History
    path('stock-movements/', views.stock_movement_list, name='stock_movement_list'),

    # User Profile & Settings
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/password/', views.password_change, name='password_change'),

    # AJAX barcode lookup
    path('ajax/get_product/', views.get_product_by_barcode, name='get_product_by_barcode'),
]

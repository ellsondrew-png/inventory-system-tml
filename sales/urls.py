from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # ---------------- Clients ----------------
    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:pk>/edit/', views.client_edit, name='client_edit'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),

    # ---------------- Quotations ----------------
    path('quotations/', views.quotation_list, name='quotation_list'),
    path('quotations/create/', views.quotation_create, name='quotation_create'),
    path('quotations/<int:pk>/', views.quotation_detail, name='quotation_detail'),  # DETAIL
    path('quotations/<int:pk>/edit/', views.quotation_edit, name='quotation_edit'),
    path('quotations/<int:pk>/delete/', views.quotation_delete, name='quotation_delete'),
    path('quotations/<int:pk>/delete-item/<int:item_id>/', views.quotation_item_delete, name='quotation_item_delete'),

    # ---------------- Invoices ----------------
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),  # DETAIL
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<int:pk>/delete-item/<int:item_id>/', views.invoice_item_delete, name='invoice_item_delete'),

    # ---------------- Delivery Notes ----------------
    path('delivery-notes/', views.delivery_note_list, name='delivery_note_list'),
    path('delivery-notes/create/', views.delivery_note_create, name='delivery_note_create'),
    path('delivery-notes/<int:pk>/', views.delivery_note_detail, name='delivery_note_detail'),  # DETAIL
    path('delivery-notes/<int:pk>/edit/', views.delivery_note_edit, name='delivery_note_edit'),
    path('delivery-notes/<int:pk>/delete/', views.delivery_note_delete, name='delivery_note_delete'),
    path('delivery-notes/<int:pk>/delete-item/<int:item_id>/', views.delivery_note_item_delete, name='delivery_note_item_delete'),

    # ---------------- Credit Notes ----------------
    path('credit-notes/', views.credit_note_list, name='credit_note_list'),
    path('credit-notes/create/', views.credit_note_create, name='credit_note_create'),
    path('credit-notes/<int:pk>/', views.credit_note_detail, name='credit_note_detail'),  # DETAIL
    path('credit-notes/<int:pk>/edit/', views.credit_note_edit, name='credit_note_edit'),
    path('credit-notes/<int:pk>/delete/', views.credit_note_delete, name='credit_note_delete'),
    path('credit-notes/<int:pk>/delete-item/<int:item_id>/', views.credit_note_item_delete, name='credit_note_item_delete'),
]

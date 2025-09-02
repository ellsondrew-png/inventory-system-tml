from django.contrib import admin
from decimal import Decimal
from .models import Client, Quotation, QuotationItem, Invoice, InvoiceItem, DeliveryNote, DeliveryNoteItem, CreditNote, CreditNoteItem


# -------------------------
# Inline Admins (for items)
# -------------------------
class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1
    readonly_fields = ("amount",)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ("amount",)


class DeliveryNoteItemInline(admin.TabularInline):
    model = DeliveryNoteItem
    extra = 1
    readonly_fields = ("amount",)


class CreditNoteItemInline(admin.TabularInline):
    model = CreditNoteItem
    extra = 1
    readonly_fields = ("amount",)


# -------------------------
# Main Admin Models
# -------------------------
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "telephone", "pin")
    search_fields = ("name", "email", "pin")


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("quotation_number", "client", "date", "subtotal_calc", "tax_calc", "total_calc", "validity_period")
    list_filter = ("date",)
    search_fields = ("quotation_number", "client__name")
    inlines = [QuotationItemInline]
    readonly_fields = ("subtotal", "tax", "total")

    def subtotal_calc(self, obj):
        return sum(item.amount for item in obj.items.all())
    subtotal_calc.short_description = "Subtotal"

    def tax_calc(self, obj):
        return sum(item.amount for item in obj.items.all()) * Decimal('0.16')
    tax_calc.short_description = "Tax"

    def total_calc(self, obj):
        subtotal = sum(item.amount for item in obj.items.all())
        return subtotal + (subtotal * Decimal('0.16'))
    total_calc.short_description = "Total"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "client", "date", "subtotal_calc", "tax_calc", "total_calc", "payment_status")
    list_filter = ("payment_status", "date")
    search_fields = ("invoice_number", "client__name")
    inlines = [InvoiceItemInline]
    readonly_fields = ("subtotal", "tax", "total")

    def subtotal_calc(self, obj):
        return sum(item.amount for item in obj.items.all())
    subtotal_calc.short_description = "Subtotal"

    def tax_calc(self, obj):
        return sum(item.amount for item in obj.items.all()) * Decimal('0.16')
    tax_calc.short_description = "Tax"

    def total_calc(self, obj):
        subtotal = sum(item.amount for item in obj.items.all())
        return subtotal + (subtotal * Decimal('0.16'))
    total_calc.short_description = "Total"


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = ("delivery_note_number", "client", "date", "subtotal_calc", "tax_calc", "total_calc")
    list_filter = ("date",)
    search_fields = ("delivery_note_number", "client__name")
    inlines = [DeliveryNoteItemInline]
    readonly_fields = ("subtotal", "tax", "total")

    def subtotal_calc(self, obj):
        return sum(item.amount for item in obj.items.all())
    subtotal_calc.short_description = "Subtotal"

    def tax_calc(self, obj):
        return sum(item.amount for item in obj.items.all()) * Decimal('0.16')
    tax_calc.short_description = "Tax"

    def total_calc(self, obj):
        subtotal = sum(item.amount for item in obj.items.all())
        return subtotal + (subtotal * Decimal('0.16'))
    total_calc.short_description = "Total"


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ("credit_note_number", "client", "date", "order_number", "subtotal_calc", "tax_calc", "total_calc", "prepared_by")
    list_filter = ("date",)
    search_fields = ("credit_note_number", "client__name", "invoice_number", "order_number")
    inlines = [CreditNoteItemInline]
    readonly_fields = ("subtotal", "tax", "total")

    def subtotal_calc(self, obj):
        return sum(item.amount for item in obj.items.all())
    subtotal_calc.short_description = "Subtotal"

    def tax_calc(self, obj):
        return sum(item.amount for item in obj.items.all()) * Decimal('0.16')
    tax_calc.short_description = "Tax"

    def total_calc(self, obj):
        subtotal = sum(item.amount for item in obj.items.all())
        return subtotal + (subtotal * Decimal('0.16'))
    total_calc.short_description = "Total"
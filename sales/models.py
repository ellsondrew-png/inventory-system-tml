from django.db import models
from decimal import Decimal


# -------------------------
# Client Model
# -------------------------
class Client(models.Model):
    name = models.CharField(max_length=255)
    po_box = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # Physical Address
    telephone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    pin = models.CharField(max_length=50, blank=True, null=True)  # KRA PIN

    def __str__(self):
        return self.name


# -------------------------
# Quotation + Items
# -------------------------
class Quotation(models.Model):
    quotation_number = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    prepared_by = models.CharField(max_length=255)  # Text input
    validity_period = models.PositiveIntegerField(default=14)  # days
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return self.quotation_number or "Draft Quotation"

    def save(self, *args, **kwargs):
        # Auto-generate quotation number
        if not self.quotation_number:
            last_qtn = Quotation.objects.order_by("id").last()
            if last_qtn and last_qtn.quotation_number:
                last_number = int(last_qtn.quotation_number.split('-')[-1])
                next_number = last_number + 1
            else:
                next_number = 3380  # start from 0500  
            self.quotation_number = f"QTN-{next_number:04d}"      

        # Calculate totals only if Quotation exists in DB and has items
        if self.pk and self.items.exists():
            subtotal = sum(item.amount for item in self.items.all())
            self.subtotal = subtotal
            self.tax = subtotal * Decimal('0.16')
            self.total = self.subtotal + self.tax
        else:
            # Default totals for new quotation
            self.subtotal = Decimal('0.00')
            self.tax = Decimal('0.00')
            self.total = Decimal('0.00')

        super().save(*args, **kwargs)


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")
    item_number = models.PositiveIntegerField(editable=False)  # sequential index
    designation = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255)  # Item Name
    brand = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    class Meta:
        ordering = ['item_number']

    def save(self, *args, **kwargs):
        # Assign item_number sequentially
        if not self.pk:
            last_item = QuotationItem.objects.filter(quotation=self.quotation).order_by("item_number").last()
            self.item_number = (int(last_item.item_number) + 1) if last_item else 1


        # Calculate amount
        self.amount = Decimal(self.quantity) * self.unit_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.item_number})"


# -------------------------
# Invoice + Items
# -------------------------
class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Overdue", "Overdue"),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_number = models.CharField(max_length=50, blank=True, null=True)
    delivery_note_number = models.CharField(max_length=50, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    prepared_by = models.CharField(max_length=255)  # Text input
    approved_by = models.CharField(max_length=255, blank=True, null=True)  # Text input
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="Pending")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return self.invoice_number or "Draft Invoice"

    def save(self, *args, **kwargs):
        # Auto-generate invoice number
        if not self.invoice_number:
            last_invoice = Invoice.objects.exclude(invoice_number__isnull=True).order_by("id").last()
            try:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
            except (ValueError, AttributeError):
                last_number = 4394  # fallback starting number
            except Exception:
                last_number = 4394  # catch any unexpected error just in case
            next_number = last_number + 1
            self.invoice_number = f"INV-{next_number:04d}"

        # Auto-calculate totals
        subtotal = sum(item.amount for item in self.items.all()) if self.pk else Decimal('0.00')
        self.subtotal = subtotal
        self.tax = subtotal * Decimal('0.16')
        self.total = self.subtotal + self.tax

        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    item_number = models.PositiveIntegerField(editable=False)  # sequential index
    designation = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            last_item = InvoiceItem.objects.filter(invoice=self.invoice).order_by("item_number").last()
            self.item_number = (int(last_item.item_number) + 1) if last_item else 1


        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.item_number})"
    
    class Meta:
        ordering = ['item_number']


# -------------------------
# Delivery Note + Items
# -------------------------
class DeliveryNote(models.Model):
    delivery_note_number = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_number = models.CharField(max_length=50, blank=True, null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="delivery_notes")
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return self.delivery_note_number or "Draft Delivery Note"

    def save(self, *args, **kwargs):
        # Auto-generate delivery note number
        if not self.delivery_note_number:
            last_dn = DeliveryNote.objects.exclude(delivery_note_number__isnull=True).order_by("id").last()
            try:
                last_number = int(last_dn.delivery_note_number.split('-')[-1])
            except (ValueError, AttributeError):
                last_number = 1555  # fallback starting number (you can choose)
            except Exception:
                last_number = 1555
            next_number = last_number + 1
            self.delivery_note_number = f"DN-{next_number:04d}"

        # Auto-calculate totals
        subtotal = sum(item.amount for item in self.items.all()) if self.pk else Decimal('0.00')
        self.subtotal = subtotal
        self.tax = subtotal * Decimal('0.16')
        self.total = self.subtotal + self.tax

        super().save(*args, **kwargs)


class DeliveryNoteItem(models.Model):
    delivery_note = models.ForeignKey(DeliveryNote, on_delete=models.CASCADE, related_name="items")
    item_number = models.PositiveIntegerField(editable=False)  # sequential index
    designation = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            last_item = DeliveryNoteItem.objects.filter(delivery_note=self.delivery_note).order_by("item_number").last()
            self.item_number = (int(last_item.item_number) + 1) if last_item else 1


        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.item_number})"
    
    class Meta:
        ordering = ['item_number']


# -------------------------
# Credit Note + Items
# -------------------------
class CreditNote(models.Model):
    credit_note_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="credit_notes")
    order_number = models.CharField(max_length=50, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    prepared_by = models.CharField(max_length=255)  # stored but not displayed on printed note
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return self.credit_note_number or "Draft Credit Note"

    def save(self, *args, **kwargs):
        # Auto-generate credit note number
        if not self.credit_note_number:
            last_cn = CreditNote.objects.exclude(credit_note_number__isnull=True).order_by("id").last()
            try:
                last_number = int(last_cn.credit_note_number.split('-')[-1])
            except (ValueError, AttributeError):
                last_number = 2211  # starting fallback (so first CN is CN-0800)
            next_number = last_number + 1
            self.credit_note_number = f"CN-{next_number:04d}"

        # Auto-calc totals from items
        subtotal = sum(item.amount for item in self.items.all()) if self.pk else Decimal('0.00')
        self.subtotal = subtotal
        self.tax = subtotal * Decimal('0.16')
        self.total = self.subtotal + self.tax

        super().save(*args, **kwargs)


class CreditNoteItem(models.Model):
    credit_note = models.ForeignKey(CreditNote, on_delete=models.CASCADE, related_name="items")
    item_number = models.PositiveIntegerField(editable=False)  # sequential index
    designation = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            last_item = CreditNoteItem.objects.filter(credit_note=self.credit_note).order_by("item_number").last()
            self.item_number = (int(last_item.item_number) + 1) if last_item else 1

        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.item_number})"

    class Meta:
        ordering = ['item_number']


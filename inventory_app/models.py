from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200, blank=True, null=True)  # Optional
    brand = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, unique=True, help_text="Scan or enter the product's barcode")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)  # <-- Optional image

    def __str__(self):
        if self.designation:
            return f"{self.name} ({self.designation})"
        return self.name


class StockMovement(models.Model):
    STOCK_IN = 'IN'
    STOCK_OUT = 'OUT'
    
    REASON_CHOICES = [
        ('Sold', 'Sold'),
        ('Damaged', 'Damaged'),
        ('Used on Site', 'Used on Site'),
        ('Modified', 'Modified'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(
        max_length=3,
        choices=[(STOCK_IN, 'Stock In'), (STOCK_OUT, 'Stock Out')]
    )
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.movement_type} - {self.product.name} ({self.quantity}) on {self.date.strftime('%Y-%m-%d')}"

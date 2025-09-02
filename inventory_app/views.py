from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .decorators import group_required
from .models import Category, Product, StockMovement
from django.contrib.auth.models import User
from django.db.models import Sum, Q, F
from django.db.models.functions import TruncMonth
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.timezone import now
from django.http import JsonResponse

# -------------------- Dashboard --------------------
@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def dashboard(request):
    categories_count = Category.objects.count()
    products_count = Product.objects.count()
    stock_movements_count = StockMovement.objects.count()
    recent_movements = StockMovement.objects.select_related("product").order_by("-date")[:5]
    low_stock_products = Product.objects.filter(quantity__lt=5)

    product_names = [p.name for p in Product.objects.all()]
    product_quantities = [p.quantity for p in Product.objects.all()]

    stock_in_count = StockMovement.objects.filter(movement_type=StockMovement.STOCK_IN).count()
    stock_out_count = StockMovement.objects.filter(movement_type=StockMovement.STOCK_OUT).count()

    current_year = now().year
    earnings_data = (
        StockMovement.objects
        .filter(movement_type=StockMovement.STOCK_OUT, date__year=current_year)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(monthly_earnings=Sum(F('quantity') * F('product__price')))
        .order_by('month')
    )

    earnings_months = [ed['month'].strftime("%b") for ed in earnings_data]
    earnings_values = [ed['monthly_earnings'] for ed in earnings_data]

    context = {
        'categories_count': categories_count,
        'products_count': products_count,
        'stock_movements_count': stock_movements_count,
        'recent_movements': recent_movements,
        'low_stock_products': low_stock_products,
        'product_names': product_names,
        'product_quantities': product_quantities,
        'stock_in_count': stock_in_count,
        'stock_out_count': stock_out_count,
        'earnings_months': earnings_months,
        'earnings_values': earnings_values,
    }
    return render(request, 'inventory_app/dashboard.html', context)

# -------------------- Category Views --------------------
@login_required
@group_required('Admin', 'Stock Clerk')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory_app/categories_list.html', {'categories': categories})

@login_required
@group_required('Admin', 'Stock Clerk')
def category_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            return redirect("category_list")
    return render(request, 'inventory_app/category_form.html')

@login_required
@group_required('Admin', 'Stock Clerk')
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            category.name = name
            category.save()
            return redirect("category_list")
    return render(request, 'inventory_app/category_form.html', {"category": category})

@login_required
@group_required('Admin', 'Stock Clerk')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        return redirect("category_list")
    return render(request, 'inventory_app/category_confirm_delete.html', {"category": category})

# -------------------- Product Views --------------------
@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(designation__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__name__icontains=query) |
            Q(barcode__icontains=query)
        )
    return render(request, 'inventory_app/products_list.html', {"products": products, "query": query})

@login_required
@group_required('Admin', 'Stock Clerk')
def product_create(request):
    categories = Category.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        designation = request.POST.get("designation")
        brand = request.POST.get("brand")
        barcode = request.POST.get("barcode")
        category_id = request.POST.get("category")
        quantity = request.POST.get("quantity")
        price = request.POST.get("price")
        image = request.FILES.get("image")  # optional

        if name and category_id:
            category = Category.objects.get(id=category_id)
            Product.objects.create(
                name=name,
                designation=designation,
                brand=brand,
                barcode=barcode,
                category=category,
                quantity=quantity,
                price=price,
                image=image
            )
            return redirect("product_list")
    return render(request, "inventory_app/product_form.html", {"categories": categories})

@login_required
@group_required('Admin', 'Stock Clerk')
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    if request.method == "POST":
        product.name = request.POST.get("name")
        product.designation = request.POST.get("designation")
        product.brand = request.POST.get("brand")
        product.barcode = request.POST.get("barcode")
        category_id = request.POST.get("category")
        product.quantity = request.POST.get("quantity")
        product.price = request.POST.get("price")
        image = request.FILES.get("image")
        if image:
            product.image = image
        if category_id:
            product.category = Category.objects.get(id=category_id)
        product.save()
        return redirect("product_list")
    return render(request, "inventory_app/product_form.html", {"product": product, "categories": categories})

@login_required
@group_required('Admin', 'Stock Clerk')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "inventory_app/product_confirm_delete.html", {"product": product})

# -------------------- Stock Management --------------------
@login_required
@group_required('Admin', 'Stock Clerk')
def stock_in(request, pk=None):
    if not pk:
        messages.error(request, "Barcode required")
        return redirect("stock_in_by_barcode")
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity"))
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity")
            return redirect("stock_in", pk=pk)

        if quantity > 0:
            product.quantity += quantity
            product.save()
            StockMovement.objects.create(
                product=product,
                movement_type=StockMovement.STOCK_IN,
                quantity=quantity,
                performed_by=request.user,
                barcode=product.barcode
            )
            messages.success(request, f"Stock added for {product.name}")
            return redirect("dashboard")
        else:
            messages.error(request, "Quantity must be greater than 0")

    return render(request, "inventory_app/stock_in.html", {"product": product})

@login_required
@group_required('Admin', 'Stock Clerk')
def stock_out(request, pk=None):
    if not pk:
        messages.error(request, "Barcode required")
        return redirect("stock_out_by_barcode")
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity"))
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity")
            return redirect("stock_out", pk=pk)

        reason = request.POST.get("reason")
        if not reason:
            messages.error(request, "Please select a reason")
            return redirect("stock_out", pk=pk)

        if 0 < quantity <= product.quantity:
            product.quantity -= quantity
            product.save()
            StockMovement.objects.create(
                product=product,
                movement_type=StockMovement.STOCK_OUT,
                quantity=quantity,
                reason=reason,
                performed_by=request.user,
                barcode=product.barcode
            )
            messages.success(request, f"Stock removed for {product.name}")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid quantity: exceeds available stock")

    return render(request, "inventory_app/stock_out.html", {"product": product, "reasons": StockMovement.REASON_CHOICES})

# -------------------- Stock In/Out by Barcode --------------------
@login_required
@group_required('Admin', 'Stock Clerk')
def stock_in_by_barcode(request):
    if request.method == "POST":
        barcode = request.POST.get("barcode")
        if barcode:
            try:
                product = Product.objects.get(barcode=barcode)
                return redirect("stock_in", pk=product.id)
            except Product.DoesNotExist:
                messages.error(request, "Product not found")
        else:
            messages.error(request, "Please enter a barcode")
    return render(request, "inventory_app/stock_in_by_barcode.html")

@login_required
@group_required('Admin', 'Stock Clerk')
def stock_out_by_barcode(request):
    if request.method == "POST":
        barcode = request.POST.get("barcode")
        if barcode:
            try:
                product = Product.objects.get(barcode=barcode)
                return redirect("stock_out", pk=product.id)
            except Product.DoesNotExist:
                messages.error(request, "Product not found")
        else:
            messages.error(request, "Please enter a barcode")
    return render(request, "inventory_app/stock_out_by_barcode.html")

# -------------------- AJAX Barcode Lookup --------------------
@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def get_product_by_barcode(request):
    barcode = request.GET.get("barcode")
    if not barcode:
        return JsonResponse({"error": "No barcode provided"})
    try:
        product = Product.objects.get(barcode=barcode)
        return JsonResponse({
            "id": product.id,
            "name": product.name,
            "designation": product.designation,
            "brand": product.brand,
            "quantity": product.quantity,
            "price": str(product.price),
            "image": product.image.url if product.image else None
        })
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"})

# -------------------- Stock Movements --------------------
@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def stock_movement_list(request):
    stock_movements = StockMovement.objects.select_related('product').order_by('-date')
    return render(request, 'inventory_app/stock_movement_list.html', {'stock_movements': stock_movements})

# -------------------- User Profile & Password --------------------
@login_required
def profile_view(request):
    return render(request, 'inventory_app/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile_view")
    return render(request, 'inventory_app/profile_edit.html', {'user': request.user})

@login_required
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("profile_view")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'inventory_app/password_change.html', {'form': form})

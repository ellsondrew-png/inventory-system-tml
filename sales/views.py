from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import group_required
from django.contrib import messages
from decimal import Decimal
from .models import Client, Quotation, QuotationItem, Invoice, InvoiceItem, DeliveryNote, DeliveryNoteItem, CreditNote, CreditNoteItem

# -----------------------------
# CLIENT VIEWS
# -----------------------------
@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'sales/client_list.html', {'clients': clients})

from .models import Client

def client_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        location = request.POST.get('location', '').strip()
        po_box = request.POST.get('po_box', '').strip()
        pin = request.POST.get('pin', '').strip()

        Client.objects.create(
            name=name,
            email=email,
            telephone=telephone,
            location=location,
            po_box=po_box,
            pin=pin
        )
        messages.success(request, "Client created successfully.")
        return redirect('sales:client_list')

    # 🚨 Pass an *empty* Client instead of None
    return render(request, 'sales/client_form.html', {'client': Client()})





def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.name = request.POST.get('name', '').strip()
        client.email = request.POST.get('email', '').strip()
        client.telephone = request.POST.get('telephone', '').strip()
        client.location = request.POST.get('location', '').strip()
        client.po_box = request.POST.get('po_box', '').strip()
        client.pin = request.POST.get('pin', '').strip()
        client.save()
        messages.success(request, "Client updated successfully.")
        return redirect('sales:client_list')

    return render(request, 'sales/client_form.html', {'client': client})


def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':  # Only delete on POST
        client.delete()
        messages.success(request, "Client deleted successfully.")
        return redirect('sales:client_list')
    
    # GET request: show confirmation page
    return render(request, 'sales/client_confirm_delete.html', {'client': client})



# -----------------------------
# QUOTATION VIEWS
# -----------------------------
@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def quotation_list(request):
    quotations = Quotation.objects.all()
    return render(request, 'sales/quotation_list.html', {'quotations': quotations})

@login_required
@group_required('Admin', 'Stock Clerk')
def quotation_create(request):
    clients = Client.objects.all()

    if request.method == 'POST':
        client_id = request.POST.get('client')
        prepared_by = request.POST.get('prepared_by', '').strip()
        validity_period = request.POST.get('validity_period')

        if not client_id:
            messages.error(request, "Please select a client.")
            return render(request, 'sales/quotation_form.html', {'clients': clients})

        client = get_object_or_404(Client, id=client_id)

        quotation = Quotation.objects.create(
            client=client,
            prepared_by=prepared_by,
            validity_period=int(validity_period) if validity_period else 14
        )

        designations = request.POST.getlist('designation')
        descriptions = request.POST.getlist('description')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')
        brands = request.POST.getlist('brand')  # NEW

        total_subtotal = Decimal('0.00')

        for desig, desc, qty, price, brand in zip(designations, descriptions, quantities, unit_prices, brands):
            if desc.strip() == "":
                continue
            qty_int = int(qty)
            price_dec = Decimal(price)
            QuotationItem.objects.create(
                quotation=quotation,
                designation=desig,
                description=desc,
                quantity=qty_int,
                unit_price=price_dec,
                brand=brand  # NEW
            )
            total_subtotal += qty_int * price_dec

        quotation.subtotal = total_subtotal
        quotation.tax = total_subtotal * Decimal('0.16')
        quotation.total = quotation.subtotal + quotation.tax
        quotation.save()

        messages.success(request, "Quotation created successfully.")
        return redirect('sales:quotation_list')

    return render(request, 'sales/quotation_form.html', {'clients': clients})


@login_required
@group_required('Admin', 'Stock Clerk')
def quotation_edit(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    clients = Client.objects.all()

    if request.method == 'POST':
        quotation.client = get_object_or_404(Client, pk=request.POST.get('client'))
        quotation.prepared_by = request.POST.get('prepared_by', '').strip()
        quotation.items.all().delete()

        designations = request.POST.getlist('designation')
        descriptions = request.POST.getlist('description')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')
        brands = request.POST.getlist('brand')  # NEW

        total_subtotal = Decimal('0.00')

        for desig, desc, qty, price, brand in zip(designations, descriptions, quantities, unit_prices, brands):
            if desc.strip():
                qty_int = int(qty)
                price_dec = Decimal(price)
                QuotationItem.objects.create(
                    quotation=quotation,
                    designation=desig,
                    description=desc,
                    quantity=qty_int,
                    unit_price=price_dec,
                    brand=brand  # NEW
                )
                total_subtotal += qty_int * price_dec

        quotation.subtotal = total_subtotal
        quotation.tax = total_subtotal * Decimal('0.16')
        quotation.total = quotation.subtotal + quotation.tax
        quotation.save()

        messages.success(request, "Quotation updated successfully.")
        return redirect('sales:quotation_list')

    return render(request, 'sales/quotation_form.html', {'quotation': quotation, 'clients': clients})


@login_required
@group_required('Admin', 'Stock Clerk')
def quotation_delete(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    if request.method == 'POST':
        quotation.delete()
        messages.success(request, "Quotation deleted successfully.")
        return redirect('sales:quotation_list')
    return render(request, 'sales/quotation_confirm_delete.html', {'quotation': quotation})


@login_required
@group_required('Admin', 'Stock Clerk')
def quotation_item_delete(request, pk, item_id):
    quotation = get_object_or_404(Quotation, pk=pk)
    item = get_object_or_404(QuotationItem, pk=item_id, quotation=quotation)
    item.delete()
    messages.success(request, "Quotation item deleted successfully.")
    return redirect('sales:quotation_edit', pk=pk)


@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    items = quotation.items.all()

    # Calculate amounts for each item and include brand
    item_amounts = []
    for item in items:
        item_amounts.append({
            'designation': item.designation,
            'description': item.description,
            'brand': item.brand,  # <--- Add this
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'amount': item.quantity * item.unit_price
        })

    # Totals
    subtotal = sum(i['amount'] for i in item_amounts)
    tax = quotation.tax if quotation.tax else 0
    total = subtotal + tax

    context = {
        'quotation': quotation,
        'item_amounts': item_amounts,
        'subtotal': subtotal,
        'tax': tax,
        'total': total
    }
    return render(request, 'sales/quotation_detail.html', context)

# -----------------------------
# INVOICE VIEWS
# -----------------------------
@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'sales/invoice_list.html', {'invoices': invoices})

@login_required
@group_required('Admin', 'Stock Clerk')
def invoice_create(request):
    clients = Client.objects.all()
    if request.method == 'POST':
        client = get_object_or_404(Client, pk=request.POST.get('client'))
        order_number = request.POST.get('order_number', '').strip()  # NEW

        invoice = Invoice.objects.create(
            client=client,
            prepared_by=request.POST.get('prepared_by', '').strip(),
            order_number=order_number  # NEW
        )

        descriptions = request.POST.getlist('description')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')
        designations = request.POST.getlist('designation')
        brands = request.POST.getlist('brand')  # NEW

        for desc, qty, price, desig, brand in zip(descriptions, quantities, unit_prices, designations, brands):
            if desc.strip():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=desc,
                    quantity=int(qty),
                    unit_price=float(price),
                    designation=desig,
                    brand=brand  # NEW
                )

        invoice.save()
        messages.success(request, "Invoice created successfully.")
        return redirect('sales:invoice_list')

    return render(request, 'sales/invoice_form.html', {'clients': clients})

@login_required
@group_required('Admin', 'Stock Clerk')
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    clients = Client.objects.all()
    if request.method == 'POST':
        invoice.client = get_object_or_404(Client, pk=request.POST.get('client'))
        invoice.order_number = request.POST.get('order_number', '').strip()  # NEW
        invoice.items.all().delete()

        descriptions = request.POST.getlist('description')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')
        designations = request.POST.getlist('designation')
        brands = request.POST.getlist('brand')  # NEW

        for desc, qty, price, desig, brand in zip(descriptions, quantities, unit_prices, designations, brands):
            if desc.strip():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=desc,
                    quantity=int(qty),
                    unit_price=float(price),
                    designation=desig,
                    brand=brand  # NEW
                )

        invoice.save()
        messages.success(request, "Invoice updated successfully.")
        return redirect('sales:invoice_list')

    return render(request, 'sales/invoice_form.html', {'invoice': invoice, 'clients': clients})



@login_required
@group_required('Admin', 'Stock Clerk')
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, "Invoice deleted successfully.")
        return redirect('sales:invoice_list')
    return render(request, 'sales/invoice_confirm_delete.html', {'invoice': invoice})

@login_required
@group_required('Admin', 'Stock Clerk')
def invoice_item_delete(request, pk, item_id):
    invoice = get_object_or_404(Invoice, pk=pk)
    item = get_object_or_404(InvoiceItem, pk=item_id, invoice=invoice)
    item.delete()
    messages.success(request, "Invoice item deleted successfully.")
    return redirect('sales:invoice_edit', pk=pk)


@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()
    return render(request, 'sales/invoice_detail.html', {'invoice': invoice, 'items': items})

# -----------------------------
# DELIVERY NOTE VIEWS
# -----------------------------
@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def delivery_note_list(request):
    notes = DeliveryNote.objects.all()
    return render(request, 'sales/delivery_note_list.html', {'notes': notes})

@login_required
@group_required('Admin', 'Stock Clerk')
def delivery_note_create(request):
    clients = Client.objects.all()
    invoices = Invoice.objects.all()

    if request.method == 'POST':
        client = get_object_or_404(Client, pk=request.POST.get('client'))
        invoice_id = request.POST.get('invoice')
        invoice = get_object_or_404(Invoice, pk=invoice_id) if invoice_id else None

        note = DeliveryNote.objects.create(
            client=client,
            invoice=invoice,
            order_number=invoice.order_number if invoice else request.POST.get('order_number', '')
        )

        items = zip(
            request.POST.getlist('designation'),
            request.POST.getlist('description'),
            request.POST.getlist('quantity'),
            request.POST.getlist('unit_price'),
            request.POST.getlist('brand')
        )

        total_subtotal = 0
        for desig, desc, qty, price, brand in items:
            if desc.strip():
                qty_int = int(qty) if qty else 0
                price_float = float(price) if price else 0
                DeliveryNoteItem.objects.create(
                    delivery_note=note,
                    designation=desig,
                    description=desc,
                    quantity=qty_int,
                    unit_price=price_float,
                    brand=brand
                )
                total_subtotal += qty_int * price_float

        # Save totals
        note.subtotal = total_subtotal
        note.tax = total_subtotal * 0.16  # 16% tax
        note.total = note.subtotal + note.tax
        note.save()

        messages.success(request, "Delivery Note created successfully.")
        return redirect('sales:delivery_note_list')

    return render(request, 'sales/delivery_note_form.html', {
        'clients': clients,
        'invoices': invoices
    })

@login_required
@group_required('Admin', 'Stock Clerk')
def delivery_note_edit(request, pk):
    note = get_object_or_404(DeliveryNote, pk=pk)
    clients = Client.objects.all()
    invoices = Invoice.objects.all()

    if request.method == 'POST':
        note.client = get_object_or_404(Client, pk=request.POST.get('client'))
        invoice_id = request.POST.get('invoice')
        note.invoice = get_object_or_404(Invoice, pk=invoice_id) if invoice_id else None

        # Handle order number
        if note.invoice:
            note.order_number = note.invoice.order_number
        else:
            note.order_number = request.POST.get('order_number', '')

        note.items.all().delete()

        items = zip(
            request.POST.getlist('designation'),
            request.POST.getlist('description'),
            request.POST.getlist('quantity'),
            request.POST.getlist('unit_price'),
            request.POST.getlist('brand')
        )

        total_subtotal = 0
        for desig, desc, qty, price, brand in items:
            if desc.strip():
                qty_int = int(qty) if qty else 0
                price_float = float(price) if price else 0
                DeliveryNoteItem.objects.create(
                    delivery_note=note,
                    designation=desig,
                    description=desc,
                    quantity=qty_int,
                    unit_price=price_float,
                    brand=brand
                )
                total_subtotal += qty_int * price_float

        # Save totals
        note.subtotal = total_subtotal
        note.tax = total_subtotal * 0.16
        note.total = note.subtotal + note.tax
        note.save()

        messages.success(request, "Delivery Note updated successfully.")
        return redirect('sales:delivery_note_list')

    return render(request, 'sales/delivery_note_form.html', {
        'note': note,
        'clients': clients,
        'invoices': invoices
    })


@login_required
@group_required('Admin', 'Stock Clerk')
def delivery_note_delete(request, pk):
    note = get_object_or_404(DeliveryNote, pk=pk)
    if request.method == 'POST':
        note.delete()
        messages.success(request, "Delivery Note deleted successfully.")
        return redirect('sales:delivery_note_list')
    return render(request, 'sales/delivery_note_confirm_delete.html', {'note': note})

@login_required
@group_required('Admin', 'Stock Clerk')
def delivery_note_item_delete(request, pk, item_id):
    note = get_object_or_404(DeliveryNote, pk=pk)
    item = get_object_or_404(DeliveryNoteItem, pk=item_id, delivery_note=note)
    item.delete()
    messages.success(request, "Delivery Note item deleted successfully.")
    return redirect('sales:delivery_note_edit', pk=pk)


@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def delivery_note_detail(request, pk):
    delivery_note = get_object_or_404(DeliveryNote, pk=pk)
    items = delivery_note.items.all()
    return render(request, 'sales/delivery_note_detail.html', {'delivery_note': delivery_note, 'items': items})


# -----------------------------
# CREDIT NOTE VIEWS
# -----------------------------
@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def credit_note_list(request):
    credit_notes = CreditNote.objects.all()
    return render(request, 'sales/credit_note_list.html', {'credit_notes': credit_notes})


@login_required
@group_required('Admin', 'Stock Clerk')
def credit_note_create(request):
    clients = Client.objects.all()
    invoices = Invoice.objects.all()  # Pass all invoices for dropdown

    if request.method == 'POST':
        client = get_object_or_404(Client, pk=request.POST.get('client'))
        invoice_id = request.POST.get('invoice')
        invoice = Invoice.objects.filter(pk=invoice_id).first() if invoice_id else None

        # Step 1: Create CreditNote (empty totals at first)
        credit_note = CreditNote.objects.create(
            client=client,
            prepared_by=request.POST.get('prepared_by', '').strip(),
            order_number=invoice.order_number if invoice else request.POST.get('order_number', '').strip(),
            invoice=invoice
        )

        # Step 2: Create items
        descriptions = request.POST.getlist('description')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')
        designations = request.POST.getlist('designation')
        brands = request.POST.getlist('brand')

        for desc, qty, price, desig, brand in zip(descriptions, quantities, unit_prices, designations, brands):
            if desc.strip():
                CreditNoteItem.objects.create(
                    credit_note=credit_note,
                    description=desc,
                    quantity=int(qty),
                    unit_price=float(price),
                    designation=desig,
                    brand=brand
                )

        # Step 3: Recalculate totals now that items exist
        subtotal = sum(item.amount for item in credit_note.items.all())
        credit_note.subtotal = subtotal
        credit_note.tax = subtotal * Decimal('0.16')
        credit_note.total = credit_note.subtotal + credit_note.tax
        credit_note.save()

        messages.success(request, "Credit Note created successfully.")
        return redirect('sales:credit_note_list')

    return render(request, 'sales/credit_note_form.html', {
        'clients': clients,
        'invoices': invoices
    })



@login_required
@group_required('Admin', 'Stock Clerk')
def credit_note_edit(request, pk):
    credit_note = get_object_or_404(CreditNote, pk=pk)
    clients = Client.objects.all()
    invoices = Invoice.objects.all()  # Pass invoices for dropdown

    if request.method == 'POST':
        credit_note.client = get_object_or_404(Client, pk=request.POST.get('client'))
        invoice_id = request.POST.get('invoice')
        invoice = Invoice.objects.filter(pk=invoice_id).first() if invoice_id else None

        credit_note.order_number = invoice.order_number if invoice else request.POST.get('order_number', '').strip()
        credit_note.invoice = invoice  # Update ForeignKey properly

        # Delete old items and recreate
        credit_note.items.all().delete()
        descriptions = request.POST.getlist('description')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')
        designations = request.POST.getlist('designation')
        brands = request.POST.getlist('brand')

        for desc, qty, price, desig, brand in zip(descriptions, quantities, unit_prices, designations, brands):
            if desc.strip():
                CreditNoteItem.objects.create(
                    credit_note=credit_note,
                    description=desc,
                    quantity=int(qty),
                    unit_price=float(price),
                    designation=desig,
                    brand=brand
                )

        credit_note.save()
        messages.success(request, "Credit Note updated successfully.")
        return redirect('sales:credit_note_list')

    return render(request, 'sales/credit_note_form.html', {
        'credit_note': credit_note,
        'clients': clients,
        'invoices': invoices
    })



@login_required
@group_required('Admin', 'Stock Clerk')
def credit_note_delete(request, pk):
    credit_note = get_object_or_404(CreditNote, pk=pk)
    if request.method == 'POST':
        credit_note.delete()
        messages.success(request, "Credit Note deleted successfully.")
        return redirect('sales:credit_note_list')
    return render(request, 'sales/credit_note_confirm_delete.html', {'credit_note': credit_note})


@login_required
@group_required('Admin', 'Stock Clerk')
def credit_note_item_delete(request, pk, item_id):
    credit_note = get_object_or_404(CreditNote, pk=pk)
    item = get_object_or_404(CreditNoteItem, pk=item_id, credit_note=credit_note)
    item.delete()
    messages.success(request, "Credit Note item deleted successfully.")
    return redirect('sales:credit_note_edit', pk=pk)


@login_required
@group_required('Admin', 'Stock Clerk', 'Viewer')
def credit_note_detail(request, pk):
    credit_note = get_object_or_404(CreditNote, pk=pk)
    items = credit_note.items.all()
    return render(request, 'sales/credit_note_detail.html', {'credit_note': credit_note, 'items': items})



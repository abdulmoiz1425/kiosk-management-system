from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Sale
from .forms import SaleForm


@login_required
def add_sale(request):
    if not request.user.kiosk:
        messages.error(request, 'You are not assigned to a kiosk.')
        return redirect('dashboard:employee')

    today = timezone.localdate()
    existing = Sale.objects.filter(kiosk=request.user.kiosk, date=today).first()

    if request.method == 'POST':
        form = SaleForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.kiosk = request.user.kiosk
            sale.recorded_by = request.user
            sale.date = today
            sale.save()
            messages.success(request, 'Daily sales saved successfully.')
            return redirect('dashboard:employee')
    else:
        form = SaleForm(instance=existing)

    return render(request, 'sales/add_sale.html', {'form': form, 'existing': existing, 'today': today})

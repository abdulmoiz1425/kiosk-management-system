from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Expense
from .forms import ExpenseForm
from core.storage import save_upload


@login_required
def add_expense(request):
    if not request.user.kiosk:
        messages.error(request, 'You are not assigned to a kiosk.')
        return redirect('dashboard:employee')

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.kiosk = request.user.kiosk
            expense.recorded_by = request.user
            expense.date = timezone.localdate()

            if 'receipt_photo' in request.FILES:
                expense.receipt_photo = save_upload(
                    request.FILES['receipt_photo'],
                    request.user.kiosk.name,
                    'expense'
                )

            expense.save()
            messages.success(request, f'Expense of {expense.amount} SAR recorded successfully.')
            return redirect('dashboard:employee')
    else:
        form = ExpenseForm()

    today_expenses = Expense.objects.filter(
        kiosk=request.user.kiosk,
        date=timezone.localdate()
    )
    return render(request, 'expenses/add_expense.html', {'form': form, 'today_expenses': today_expenses})

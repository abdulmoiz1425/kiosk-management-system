from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
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


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, recorded_by=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            updated = form.save(commit=False)
            if 'receipt_photo' in request.FILES:
                updated.receipt_photo = save_upload(
                    request.FILES['receipt_photo'],
                    expense.kiosk.name,
                    'expense'
                )
            updated.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('expenses:add')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form, 'expense': expense})


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, recorded_by=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('expenses:add')
    return render(request, 'expenses/confirm_delete.html', {'expense': expense})

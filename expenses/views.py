from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Expense, NoExpenseDay
from .forms import ExpenseForm
from core.storage import save_upload


@login_required
def add_expense(request):
    if not request.user.kiosk:
        messages.error(request, 'You are not assigned to a kiosk.')
        return redirect('dashboard:employee')

    today = timezone.localdate()
    kiosk = request.user.kiosk
    no_expense_day = NoExpenseDay.objects.filter(kiosk=kiosk, date=today).first()

    if request.method == 'POST':
        if no_expense_day:
            messages.error(request, 'Cannot add expenses — "No Expenses" is recorded for today.')
            return redirect('expenses:add')

        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.kiosk = kiosk
            expense.recorded_by = request.user
            expense.date = today

            if 'receipt_photo' in request.FILES:
                expense.receipt_photo = save_upload(
                    request.FILES['receipt_photo'],
                    kiosk.name,
                    'expense'
                )

            expense.save()
            messages.success(request, f'Expense of {expense.amount} recorded successfully.')
            return redirect('expenses:add')
    else:
        form = ExpenseForm()

    today_expenses = Expense.objects.filter(kiosk=kiosk, date=today)
    return render(request, 'expenses/add_expense.html', {
        'form': form,
        'today_expenses': today_expenses,
        'no_expense_day': no_expense_day,
    })


@login_required
def toggle_no_expense(request):
    if request.method != 'POST':
        return redirect('expenses:add')
    if not request.user.kiosk:
        return redirect('dashboard:employee')

    today = timezone.localdate()
    kiosk = request.user.kiosk
    existing = NoExpenseDay.objects.filter(kiosk=kiosk, date=today).first()

    if existing:
        existing.delete()
        messages.info(request, 'No Expenses removed — you can now add expenses.')
    else:
        # Block if expenses already exist today
        if Expense.objects.filter(kiosk=kiosk, date=today).exists():
            messages.error(request, 'Cannot mark "No Expenses" — expenses already recorded today.')
        else:
            NoExpenseDay.objects.create(kiosk=kiosk, recorded_by=request.user, date=today)
            messages.success(request, '"No Expenses" recorded for today.')

    return redirect('expenses:add')


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

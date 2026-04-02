from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from attendance.models import Attendance
from sales.models import Sale
from expenses.models import Expense
from reports.models import DailyReport


@login_required
def home(request):
    user = request.user
    if user.is_owner:
        return redirect('owner:dashboard')
    elif user.is_supervisor:
        return redirect('supervisor:dashboard')
    else:
        return redirect('dashboard:employee')


@login_required
def owner_dashboard(request):
    if not request.user.is_owner:
        return redirect('dashboard:home')
    return render(request, 'dashboard/owner.html', {'today': timezone.localdate()})


@login_required
def supervisor_dashboard(request):
    if request.user.is_employee:
        return redirect('dashboard:home')
    return render(request, 'dashboard/supervisor.html', {'today': timezone.localdate()})


@login_required
def employee_dashboard(request):
    today = timezone.localdate()
    context = {'today': today}

    if request.user.kiosk:
        attendance = Attendance.objects.filter(employee=request.user, date=today).first()
        sale = Sale.objects.filter(kiosk=request.user.kiosk, date=today).first()
        expenses = Expense.objects.filter(kiosk=request.user.kiosk, date=today)
        report = DailyReport.objects.filter(kiosk=request.user.kiosk, date=today).first()

        context.update({
            'attendance': attendance,
            'sale': sale,
            'expenses': expenses,
            'total_expenses': sum(e.amount for e in expenses),
            'report': report,
        })

    return render(request, 'dashboard/employee.html', context)


@login_required
def employee_history(request):
    attendances = Attendance.objects.filter(employee=request.user).order_by('-date')[:30]
    sales = Sale.objects.filter(recorded_by=request.user).order_by('-date')[:30]
    expenses = Expense.objects.filter(recorded_by=request.user).order_by('-date')[:30]
    reports = DailyReport.objects.filter(submitted_by=request.user).order_by('-date')[:30]

    return render(request, 'dashboard/history.html', {
        'attendances': attendances,
        'sales': sales,
        'expenses': expenses,
        'reports': reports,
        'today': timezone.localdate(),
    })

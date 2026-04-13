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


def _fmt_hours(seconds):
    """Convert seconds to '8h 30m' string."""
    if seconds is None or seconds <= 0:
        return '—'
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m:02d}m"


@login_required
def employee_history(request):
    raw_attendances = Attendance.objects.filter(employee=request.user).order_by('-date')[:30]
    sales      = Sale.objects.filter(recorded_by=request.user).order_by('-date')[:30]
    expenses   = Expense.objects.filter(recorded_by=request.user).order_by('-date')[:30]
    reports    = DailyReport.objects.filter(submitted_by=request.user).order_by('-date')[:30]

    STANDARD_HOURS = 10 * 3600  # 10 hrs in seconds

    attendances = []
    total_worked_sec  = 0
    total_overtime_sec = 0

    for a in raw_attendances:
        worked_sec   = None
        overtime_sec = None

        if a.check_in_time and a.check_out_time:
            diff = (a.check_out_time - a.check_in_time).total_seconds()
            if diff > 0:
                worked_sec   = diff
                overtime_sec = max(0, diff - STANDARD_HOURS)
                total_worked_sec   += worked_sec
                total_overtime_sec += overtime_sec

        attendances.append({
            'record':        a,
            'worked_fmt':    _fmt_hours(worked_sec),
            'overtime_fmt':  _fmt_hours(overtime_sec),
        })

    return render(request, 'dashboard/history.html', {
        'attendances':          attendances,
        'monthly_worked_fmt':   _fmt_hours(total_worked_sec),
        'monthly_overtime_fmt': _fmt_hours(total_overtime_sec),
        'sales':    sales,
        'expenses': expenses,
        'reports':  reports,
        'today':    timezone.localdate(),
    })

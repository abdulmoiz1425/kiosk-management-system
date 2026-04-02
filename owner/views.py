from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
from decimal import Decimal

from accounts.decorators import owner_required
from accounts.models import User
from kiosks.models import Kiosk
from attendance.models import Attendance
from sales.models import Sale
from expenses.models import Expense
from reports.models import DailyReport
from supervisor.models import SupervisorVisit, BonusPenalty


@login_required
@owner_required
def dashboard(request):
    today = timezone.localdate()

    kiosks = Kiosk.objects.filter(is_active=True)
    total_kiosks = kiosks.count()
    total_employees = User.objects.filter(role='employee').count()

    checked_in_today = Attendance.objects.filter(
        date=today, check_in_time__isnull=False
    ).values('employee').distinct().count()

    today_sales = Sale.objects.filter(date=today).aggregate(
        cash=Sum('cash_amount'), bank=Sum('bank_transfer_amount')
    )
    total_sales_today = (today_sales['cash'] or 0) + (today_sales['bank'] or 0)

    total_expenses_today = Expense.objects.filter(date=today).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Per-kiosk status
    kiosk_rows = []
    for k in kiosks:
        emps = k.employees.filter(role='employee')
        checked = Attendance.objects.filter(
            kiosk=k, date=today, check_in_time__isnull=False
        ).count()
        sale = Sale.objects.filter(kiosk=k, date=today).first()
        exp_total = Expense.objects.filter(kiosk=k, date=today).aggregate(
            t=Sum('amount')
        )['t'] or 0
        report = DailyReport.objects.filter(kiosk=k, date=today).exists()
        kiosk_rows.append({
            'kiosk': k,
            'emp_count': emps.count(),
            'checked_in': checked,
            'sale': sale,
            'expenses': exp_total,
            'report_submitted': report,
        })

    return render(request, 'owner/dashboard.html', {
        'today': today,
        'total_kiosks': total_kiosks,
        'total_employees': total_employees,
        'checked_in_today': checked_in_today,
        'total_sales_today': total_sales_today,
        'total_expenses_today': total_expenses_today,
        'kiosk_rows': kiosk_rows,
    })


@login_required
@owner_required
def attendance_overview(request):
    today = timezone.localdate()
    # Default to current month
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    from_date = today.replace(year=year, month=month, day=1)
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    to_date = from_date.replace(day=last_day)

    employees = User.objects.filter(role='employee').select_related('kiosk')
    rows = []
    for emp in employees:
        records = Attendance.objects.filter(
            employee=emp, date__gte=from_date, date__lte=to_date
        )
        present = records.filter(check_in_time__isnull=False).count()
        full_day = records.filter(
            check_in_time__isnull=False, check_out_time__isnull=False
        ).count()
        rows.append({
            'employee': emp,
            'present': present,
            'full_day': full_day,
            'absent': last_day - present,
        })

    return render(request, 'owner/attendance_overview.html', {
        'rows': rows,
        'month_label': from_date.strftime('%B %Y'),
        'year': year,
        'month': month,
        'today': today,
        'prev_month': (month - 2) % 12 + 1,
        'prev_year': year - 1 if month == 1 else year,
        'next_month': month % 12 + 1,
        'next_year': year + 1 if month == 12 else year,
    })


@login_required
@owner_required
def supervisor_visits(request):
    visits = SupervisorVisit.objects.select_related(
        'supervisor', 'kiosk'
    ).order_by('-date')

    # Filter by kiosk
    kiosk_id = request.GET.get('kiosk')
    if kiosk_id:
        visits = visits.filter(kiosk_id=kiosk_id)

    kiosks = Kiosk.objects.filter(is_active=True)
    return render(request, 'owner/supervisor_visits.html', {
        'visits': visits,
        'kiosks': kiosks,
        'selected_kiosk': kiosk_id,
        'today': timezone.localdate(),
    })


@login_required
@owner_required
def monthly_report(request):
    today = timezone.localdate()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    import calendar
    from_date = today.replace(year=year, month=month, day=1)
    last_day = calendar.monthrange(year, month)[1]
    to_date = from_date.replace(day=last_day)
    month_label = from_date.strftime('%B %Y')

    kiosks = Kiosk.objects.filter(is_active=True)

    # --- Financial summary per kiosk ---
    financial_rows = []
    grand_sales = Decimal('0')
    grand_expenses = Decimal('0')
    for k in kiosks:
        sales = Sale.objects.filter(kiosk=k, date__gte=from_date, date__lte=to_date)
        s = sales.aggregate(
            cash=Sum('cash_amount'), bank=Sum('bank_transfer_amount')
        )
        total_sales = (s['cash'] or 0) + (s['bank'] or 0)

        exp = Expense.objects.filter(
            kiosk=k, date__gte=from_date, date__lte=to_date
        ).aggregate(t=Sum('amount'))['t'] or 0

        grand_sales += Decimal(str(total_sales))
        grand_expenses += Decimal(str(exp))
        financial_rows.append({
            'kiosk': k,
            'sales': total_sales,
            'expenses': exp,
            'net': Decimal(str(total_sales)) - Decimal(str(exp)),
        })

    # --- Attendance summary per employee ---
    employees = User.objects.filter(role='employee').select_related('kiosk')
    attendance_rows = []
    for emp in employees:
        records = Attendance.objects.filter(
            employee=emp, date__gte=from_date, date__lte=to_date
        )
        present = records.filter(check_in_time__isnull=False).count()
        attendance_rows.append({
            'employee': emp,
            'present': present,
            'absent': last_day - present,
        })

    # --- Performance (supervisor visits avg rating per kiosk) ---
    perf_rows = []
    for k in kiosks:
        avg = SupervisorVisit.objects.filter(
            kiosk=k, date__gte=from_date, date__lte=to_date
        ).aggregate(avg=Avg('rating'))['avg']
        visit_count = SupervisorVisit.objects.filter(
            kiosk=k, date__gte=from_date, date__lte=to_date
        ).count()
        perf_rows.append({
            'kiosk': k,
            'visit_count': visit_count,
            'avg_rating': round(avg, 1) if avg else None,
        })

    return render(request, 'owner/monthly_report.html', {
        'month_label': month_label,
        'year': year,
        'month': month,
        'from_date': from_date,
        'to_date': to_date,
        'financial_rows': financial_rows,
        'grand_sales': grand_sales,
        'grand_expenses': grand_expenses,
        'grand_net': grand_sales - grand_expenses,
        'attendance_rows': attendance_rows,
        'perf_rows': perf_rows,
        'today': today,
        'prev_month': (month - 2) % 12 + 1,
        'prev_year': year - 1 if month == 1 else year,
        'next_month': month % 12 + 1,
        'next_year': year + 1 if month == 12 else year,
    })


@login_required
@owner_required
def kiosk_detail(request, kiosk_id):
    kiosk = get_object_or_404(Kiosk, id=kiosk_id)
    today = timezone.localdate()
    this_month = today.replace(day=1)

    recent_sales = Sale.objects.filter(
        kiosk=kiosk, date__gte=this_month
    ).order_by('-date')
    recent_expenses = Expense.objects.filter(
        kiosk=kiosk, date__gte=this_month
    ).order_by('-date')
    recent_attendance = Attendance.objects.filter(
        kiosk=kiosk, date__gte=this_month
    ).select_related('employee').order_by('-date')
    recent_visits = SupervisorVisit.objects.filter(
        kiosk=kiosk
    ).select_related('supervisor').order_by('-date')[:10]
    employees = kiosk.employees.filter(role='employee')

    month_sales = recent_sales.aggregate(
        cash=Sum('cash_amount'), bank=Sum('bank_transfer_amount')
    )
    total_month_sales = (month_sales['cash'] or 0) + (month_sales['bank'] or 0)
    total_month_expenses = recent_expenses.aggregate(
        t=Sum('amount')
    )['t'] or 0

    return render(request, 'owner/kiosk_detail.html', {
        'kiosk': kiosk,
        'employees': employees,
        'recent_sales': recent_sales,
        'recent_expenses': recent_expenses,
        'recent_attendance': recent_attendance,
        'recent_visits': recent_visits,
        'total_month_sales': total_month_sales,
        'total_month_expenses': total_month_expenses,
        'today': today,
    })

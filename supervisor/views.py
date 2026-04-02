from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count, Sum

from accounts.decorators import supervisor_required
from accounts.models import User
from kiosks.models import Kiosk
from attendance.models import Attendance
from sales.models import Sale
from expenses.models import Expense
from .models import SupervisorVisit, BonusPenalty
from reports.models import DailyReport
from .forms import VisitForm, BonusPenaltyForm


@login_required
@supervisor_required
def dashboard(request):
    today = timezone.localdate()
    this_month_start = today.replace(day=1)

    visits_this_month = SupervisorVisit.objects.filter(
        supervisor=request.user,
        date__gte=this_month_start,
    )
    avg_rating = visits_this_month.aggregate(avg=Avg('rating'))['avg']
    bp_this_month = BonusPenalty.objects.filter(
        issued_by=request.user,
        date__gte=this_month_start,
    ).count()

    recent_visits = SupervisorVisit.objects.filter(
        supervisor=request.user
    ).select_related('kiosk')[:10]

    # Only kiosks assigned to this supervisor
    kiosks = request.user.assigned_kiosks.filter(is_active=True).prefetch_related('employees')
    kiosk_status = []
    for kiosk in kiosks:
        employees = kiosk.employees.filter(role='employee')
        checked_in = Attendance.objects.filter(
            kiosk=kiosk, date=today, check_in_time__isnull=False
        ).count()
        sale = Sale.objects.filter(kiosk=kiosk, date=today).first()
        kiosk_status.append({
            'kiosk': kiosk,
            'total_employees': employees.count(),
            'checked_in': checked_in,
            'sale': sale,
        })

    return render(request, 'supervisor/dashboard.html', {
        'today': today,
        'visits_count': visits_this_month.count(),
        'avg_rating': round(avg_rating, 1) if avg_rating else None,
        'bp_count': bp_this_month,
        'recent_visits': recent_visits,
        'kiosk_status': kiosk_status,
    })


@login_required
@supervisor_required
def log_visit(request):
    if request.method == 'POST':
        form = VisitForm(request.POST, supervisor=request.user)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.supervisor = request.user
            visit.save()
            messages.success(request, f'Visit to {visit.kiosk.name} logged — Rating: {visit.rating}/5')
            return redirect('supervisor:visits')
    else:
        form = VisitForm(supervisor=request.user, initial={'date': timezone.localdate()})

    return render(request, 'supervisor/log_visit.html', {'form': form})


@login_required
@supervisor_required
def visits_list(request):
    visits = SupervisorVisit.objects.filter(
        supervisor=request.user
    ).select_related('kiosk').order_by('-date')

    return render(request, 'supervisor/visits_list.html', {
        'visits': visits,
        'today': timezone.localdate(),
    })


@login_required
@supervisor_required
def edit_visit(request, visit_id):
    visit = get_object_or_404(SupervisorVisit, id=visit_id, supervisor=request.user)
    if request.method == 'POST':
        form = VisitForm(request.POST, instance=visit, supervisor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Visit updated successfully.')
            return redirect('supervisor:visits')
    else:
        form = VisitForm(instance=visit, supervisor=request.user)
    return render(request, 'supervisor/log_visit.html', {'form': form, 'edit': True, 'visit': visit})


@login_required
@supervisor_required
def delete_visit(request, visit_id):
    visit = get_object_or_404(SupervisorVisit, id=visit_id, supervisor=request.user)
    if request.method == 'POST':
        visit.delete()
        messages.success(request, 'Visit deleted.')
        return redirect('supervisor:visits')
    return render(request, 'supervisor/confirm_delete.html', {
        'object_name': f'{visit.kiosk.name} — {visit.date}',
        'cancel_url': 'supervisor:visits',
    })


@login_required
@supervisor_required
def add_bonus_penalty(request):
    if request.method == 'POST':
        form = BonusPenaltyForm(request.POST, supervisor=request.user)
        if form.is_valid():
            bp = form.save(commit=False)
            bp.issued_by = request.user
            bp.save()
            messages.success(request, f'{bp.get_type_display()} of {bp.amount} SAR issued to {bp.employee.get_full_name() or bp.employee.username}.')
            return redirect('supervisor:bonus_penalty')
    else:
        form = BonusPenaltyForm(supervisor=request.user, initial={'date': timezone.localdate()})

    recent = BonusPenalty.objects.filter(
        issued_by=request.user
    ).select_related('employee').order_by('-date')[:20]

    return render(request, 'supervisor/bonus_penalty.html', {
        'form': form,
        'recent': recent,
    })


@login_required
@supervisor_required
def edit_bonus_penalty(request, bp_id):
    bp = get_object_or_404(BonusPenalty, id=bp_id, issued_by=request.user)
    if request.method == 'POST':
        form = BonusPenaltyForm(request.POST, instance=bp, supervisor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record updated successfully.')
            return redirect('supervisor:bonus_penalty')
    else:
        form = BonusPenaltyForm(instance=bp, supervisor=request.user)
    return render(request, 'supervisor/bonus_penalty.html', {'form': form, 'edit': True, 'bp': bp, 'recent': []})


@login_required
@supervisor_required
def delete_bonus_penalty(request, bp_id):
    bp = get_object_or_404(BonusPenalty, id=bp_id, issued_by=request.user)
    if request.method == 'POST':
        bp.delete()
        messages.success(request, 'Record deleted.')
        return redirect('supervisor:bonus_penalty')
    return render(request, 'supervisor/confirm_delete.html', {
        'object_name': f'{bp.get_type_display()} — {bp.employee.get_full_name() or bp.employee.username} — {bp.amount} SAR',
        'cancel_url': 'supervisor:bonus_penalty',
    })


@login_required
@supervisor_required
def employee_performance(request):
    assigned_kiosks = request.user.assigned_kiosks.all()
    employees = User.objects.filter(role='employee', kiosk__in=assigned_kiosks).select_related('kiosk')
    today = timezone.localdate()
    this_month_start = today.replace(day=1)

    perf_data = []
    for emp in employees:
        attendance_count = Attendance.objects.filter(
            employee=emp,
            date__gte=this_month_start,
            check_in_time__isnull=False,
        ).count()

        total_sales = Sale.objects.filter(
            recorded_by=emp,
            date__gte=this_month_start,
        ).aggregate(total=Sum('cash_amount') + Sum('bank_transfer_amount'))['total'] or 0

        avg_visit_rating = SupervisorVisit.objects.filter(
            kiosk=emp.kiosk,
            date__gte=this_month_start,
        ).aggregate(avg=Avg('rating'))['avg']

        bonus = BonusPenalty.objects.filter(
            employee=emp,
            type='bonus',
            date__gte=this_month_start,
        ).aggregate(total=Sum('amount'))['total'] or 0

        penalty = BonusPenalty.objects.filter(
            employee=emp,
            type='penalty',
            date__gte=this_month_start,
        ).aggregate(total=Sum('amount'))['total'] or 0

        perf_data.append({
            'employee': emp,
            'attendance_days': attendance_count,
            'total_sales': total_sales,
            'avg_rating': round(avg_visit_rating, 1) if avg_visit_rating else None,
            'bonus': bonus,
            'penalty': penalty,
        })

    return render(request, 'supervisor/employee_performance.html', {
        'perf_data': perf_data,
        'month': this_month_start.strftime('%B %Y'),
        'today': today,
    })


@login_required
@supervisor_required
def employee_detail(request, user_id):
    if request.user.is_owner:
        employee = get_object_or_404(User, id=user_id, role='employee')
    else:
        assigned_kiosks = request.user.assigned_kiosks.all()
        employee = get_object_or_404(User, id=user_id, role='employee', kiosk__in=assigned_kiosks)
    today = timezone.localdate()

    attendances = Attendance.objects.filter(employee=employee).order_by('-date')[:30]
    sales = Sale.objects.filter(recorded_by=employee).order_by('-date')[:30]
    expenses = Expense.objects.filter(recorded_by=employee).order_by('-date')[:30]
    bonus_penalties = BonusPenalty.objects.filter(employee=employee).order_by('-date')[:20]
    reports = DailyReport.objects.filter(submitted_by=employee).order_by('-date')[:30]

    return render(request, 'supervisor/employee_detail.html', {
        'employee': employee,
        'attendances': attendances,
        'sales': sales,
        'expenses': expenses,
        'bonus_penalties': bonus_penalties,
        'reports': reports,
        'today': today,
    })

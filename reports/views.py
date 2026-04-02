from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .models import DailyReport
from .forms import DailyReportForm
from core.storage import save_upload
from sales.models import Sale
from expenses.models import Expense


@login_required
def submit_report(request):
    if not request.user.kiosk:
        messages.error(request, 'You are not assigned to a kiosk.')
        return redirect('dashboard:employee')

    today = timezone.localdate()
    kiosk = request.user.kiosk
    existing = DailyReport.objects.filter(kiosk=kiosk, date=today).first()

    if existing:
        messages.info(request, 'Daily report already submitted for today.')
        return redirect('dashboard:employee')

    # Sales & expense summary for context
    sale = Sale.objects.filter(kiosk=kiosk, date=today).first()
    today_expenses = Expense.objects.filter(kiosk=kiosk, date=today).order_by('category')
    total_expenses = today_expenses.aggregate(total=Sum('amount'))['total'] or 0

    if request.method == 'POST':
        form = DailyReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.kiosk = kiosk
            report.submitted_by = request.user
            report.date = today

            if 'opening_photo' in request.FILES:
                report.opening_photo = save_upload(
                    request.FILES['opening_photo'],
                    kiosk.name,
                    'opening'
                )
            if 'closing_photo' in request.FILES:
                report.closing_photo = save_upload(
                    request.FILES['closing_photo'],
                    kiosk.name,
                    'closing'
                )

            report.save()
            messages.success(request, 'Daily report submitted successfully. Good work today!')
            return redirect('dashboard:employee')
    else:
        form = DailyReportForm()

    return render(request, 'reports/submit_report.html', {
        'form': form,
        'today': today,
        'sale': sale,
        'today_expenses': today_expenses,
        'total_expenses': total_expenses,
    })

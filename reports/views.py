from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import DailyReport
from .forms import DailyReportForm
from core.storage import save_upload


@login_required
def submit_report(request):
    if not request.user.kiosk:
        messages.error(request, 'You are not assigned to a kiosk.')
        return redirect('dashboard:employee')

    today = timezone.localdate()
    existing = DailyReport.objects.filter(kiosk=request.user.kiosk, date=today).first()

    if existing:
        messages.info(request, 'Daily report already submitted for today.')
        return redirect('dashboard:employee')

    if request.method == 'POST':
        form = DailyReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.kiosk = request.user.kiosk
            report.submitted_by = request.user
            report.date = today

            if 'closing_photo' in request.FILES:
                report.closing_photo = save_upload(
                    request.FILES['closing_photo'],
                    request.user.kiosk.name,
                    'closing'
                )

            report.save()
            messages.success(request, 'Daily report submitted successfully. Good work today!')
            return redirect('dashboard:employee')
    else:
        form = DailyReportForm()

    return render(request, 'reports/submit_report.html', {'form': form, 'today': today})

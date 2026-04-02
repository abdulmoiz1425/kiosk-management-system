from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Attendance
from .forms import CheckInForm, CheckOutForm
from core.storage import save_upload


@login_required
def checkin(request):
    if not request.user.kiosk:
        messages.error(request, 'You are not assigned to a kiosk. Contact your supervisor.')
        return redirect('dashboard:employee')

    today = timezone.localdate()
    attendance, _ = Attendance.objects.get_or_create(
        employee=request.user,
        date=today,
        defaults={'kiosk': request.user.kiosk}
    )

    if attendance.check_in_time:
        if attendance.check_out_time:
            messages.info(request, 'Already done. Check-in and Check-out completed for today.')
            return redirect('dashboard:employee')
        return redirect('attendance:checkout')

    if request.method == 'POST':
        form = CheckInForm(request.POST, request.FILES)
        if form.is_valid():
            rel_path = save_upload(request.FILES['photo'], request.user.kiosk.name, 'checkin')
            attendance.check_in_time = timezone.now()
            attendance.check_in_photo = rel_path
            attendance.notes = form.cleaned_data.get('notes', '')
            attendance.save()
            messages.success(request, f'Checked in at {attendance.check_in_time.strftime("%H:%M")}. Have a great day!')
            return redirect('dashboard:employee')
    else:
        form = CheckInForm()

    return render(request, 'attendance/checkin.html', {'form': form})


@login_required
def checkout(request):
    if not request.user.kiosk:
        messages.error(request, 'You are not assigned to a kiosk.')
        return redirect('dashboard:employee')

    today = timezone.localdate()
    try:
        attendance = Attendance.objects.get(employee=request.user, date=today)
    except Attendance.DoesNotExist:
        messages.error(request, 'You have not checked in today.')
        return redirect('dashboard:employee')

    if not attendance.check_in_time:
        messages.error(request, 'You have not checked in today.')
        return redirect('dashboard:employee')

    if attendance.check_out_time:
        messages.info(request, f'Already checked out at {attendance.check_out_time.strftime("%H:%M")}.')
        return redirect('dashboard:employee')

    if request.method == 'POST':
        form = CheckOutForm(request.POST, request.FILES)
        if form.is_valid():
            rel_path = save_upload(request.FILES['photo'], request.user.kiosk.name, 'checkout')
            attendance.check_out_time = timezone.now()
            attendance.check_out_photo = rel_path
            attendance.save()
            messages.success(request, f'Checked out at {attendance.check_out_time.strftime("%H:%M")}. See you tomorrow!')
            return redirect('dashboard:employee')
    else:
        form = CheckOutForm()

    return render(request, 'attendance/checkout.html', {'form': form, 'attendance': attendance})

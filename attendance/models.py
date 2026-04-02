from django.db import models
from django.conf import settings


class Attendance(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances',
    )
    kiosk = models.ForeignKey(
        'kiosks.Kiosk',
        on_delete=models.CASCADE,
        related_name='attendances',
    )
    date = models.DateField()
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_in_photo = models.ImageField(upload_to='', blank=True)  # path set by storage handler
    check_out_time = models.DateTimeField(null=True, blank=True)
    check_out_photo = models.ImageField(upload_to='', blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} — {self.date}"

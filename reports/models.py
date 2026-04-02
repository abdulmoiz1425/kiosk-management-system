from django.db import models
from django.conf import settings


class DailyReport(models.Model):
    kiosk = models.ForeignKey(
        'kiosks.Kiosk',
        on_delete=models.CASCADE,
        related_name='daily_reports',
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_reports',
    )
    date = models.DateField()
    opening_photo = models.ImageField(upload_to='', blank=True)  # path set by storage handler
    closing_photo = models.ImageField(upload_to='', blank=True)  # path set by storage handler
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('kiosk', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.kiosk} — {self.date}"

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
    opening_photo = models.ImageField(
        upload_to='', blank=True,
        verbose_name='Report Generator (Main Photo)')
    closing_photo = models.ImageField(
        upload_to='', blank=True,
        verbose_name='Shift Report')
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('kiosk', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.kiosk} — {self.date}"


class ReportPhoto(models.Model):
    """Additional photos uploaded under Report Generator."""
    report = models.ForeignKey(
        DailyReport,
        on_delete=models.CASCADE,
        related_name='extra_photos',
    )
    photo = models.ImageField(upload_to='reports/extra/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.report}"

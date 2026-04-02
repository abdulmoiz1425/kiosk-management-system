from django.db import models
from django.conf import settings


class Expense(models.Model):
    class Category(models.TextChoices):
        SUPPLIES = 'supplies', 'Supplies'
        MAINTENANCE = 'maintenance', 'Maintenance'
        TRANSPORT = 'transport', 'Transport'
        OTHER = 'other', 'Other'

    kiosk = models.ForeignKey(
        'kiosks.Kiosk',
        on_delete=models.CASCADE,
        related_name='expenses',
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses',
    )
    date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    receipt_photo = models.ImageField(upload_to='', blank=True)  # path set by storage handler
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.kiosk} — {self.category} — {self.amount}"

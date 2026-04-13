from django.db import models
from django.conf import settings


class Sale(models.Model):
    kiosk = models.ForeignKey(
        'kiosks.Kiosk',
        on_delete=models.CASCADE,
        related_name='sales',
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sales',
    )
    date = models.DateField()
    starting_cash        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_amount          = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # Cash Payments
    bank_transfer_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # QR Bank Account
    actual_cash          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cashier_photo        = models.ImageField(upload_to='sales/cashier/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('kiosk', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.kiosk} — {self.date}"

    @property
    def expected_cash(self):
        return self.starting_cash + self.cash_amount

    @property
    def difference(self):
        return self.actual_cash - self.expected_cash

    @property
    def total(self):
        return self.cash_amount + self.bank_transfer_amount

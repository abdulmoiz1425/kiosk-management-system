from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class SupervisorVisit(models.Model):
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visits',
    )
    kiosk = models.ForeignKey(
        'kiosks.Kiosk',
        on_delete=models.CASCADE,
        related_name='supervisor_visits',
    )
    date = models.DateField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.supervisor} visited {self.kiosk} on {self.date} — {self.rating}/5"


class BonusPenalty(models.Model):
    class Type(models.TextChoices):
        BONUS = 'bonus', 'Bonus'
        PENALTY = 'penalty', 'Penalty'

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bonus_penalties',
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issued_bonus_penalties',
    )
    type = models.CharField(max_length=10, choices=Type.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Bonus / Penalties'

    def __str__(self):
        return f"{self.get_type_display()} — {self.employee} — {self.amount}"

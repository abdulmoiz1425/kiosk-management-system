import os
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


EVAL_RATING_VALIDATORS = [MinValueValidator(1), MaxValueValidator(5)]
EVAL_RATING_CHOICES = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]


def visit_photo_path(instance, filename):
    """Store visit photos in: visits/DD-Mon-YYYY - Kiosk Name/filename"""
    date_str  = instance.date.strftime('%d-%b-%Y') if instance.date else 'unknown-date'
    kiosk_name = instance.kiosk.name if instance.kiosk_id else 'unknown-kiosk'
    folder = f"{date_str} - {kiosk_name}"
    return os.path.join('visits', folder, filename)


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

    # Evaluation Categories
    attendance_rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=EVAL_RATING_VALIDATORS)
    attendance_photo = models.ImageField(
        upload_to=visit_photo_path, null=True, blank=True)

    cleanliness_rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=EVAL_RATING_VALIDATORS)
    cleanliness_photo = models.ImageField(
        upload_to=visit_photo_path, null=True, blank=True)

    device_care_rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=EVAL_RATING_VALIDATORS)
    device_care_photo = models.ImageField(
        upload_to=visit_photo_path, null=True, blank=True)

    customer_service_rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=EVAL_RATING_VALIDATORS)
    customer_service_photo = models.ImageField(
        upload_to=visit_photo_path, null=True, blank=True)

    marketing_rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=EVAL_RATING_VALIDATORS)
    marketing_photo = models.ImageField(
        upload_to=visit_photo_path, null=True, blank=True)

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

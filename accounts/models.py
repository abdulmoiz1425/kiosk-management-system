
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        SUPERVISOR = 'supervisor', 'Supervisor'
        EMPLOYEE = 'employee', 'Employee'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    kiosk = models.ForeignKey(
        'kiosks.Kiosk',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
    )
    assigned_kiosks = models.ManyToManyField(
        'kiosks.Kiosk',
        blank=True,
        related_name='assigned_supervisors',
        help_text='Kiosks this supervisor is responsible for monitoring.',
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_supervisor(self):
        return self.role == self.Role.SUPERVISOR

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

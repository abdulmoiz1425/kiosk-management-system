from django.db import models


class Kiosk(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.location}"

    class Meta:
        ordering = ['name']

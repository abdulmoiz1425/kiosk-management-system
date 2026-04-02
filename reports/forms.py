from django import forms
from .models import DailyReport


class DailyReportForm(forms.ModelForm):
    class Meta:
        model = DailyReport
        fields = ['closing_photo', 'notes']
        widgets = {
            'closing_photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'capture': 'environment',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'End of day notes, observations, issues...',
            }),
        }

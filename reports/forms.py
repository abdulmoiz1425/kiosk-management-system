from django import forms
from .models import DailyReport

_photo_widget = lambda: forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})


class DailyReportForm(forms.ModelForm):
    class Meta:
        model = DailyReport
        fields = ['opening_photo', 'closing_photo', 'notes']
        widgets = {
            'opening_photo': _photo_widget(),
            'closing_photo': _photo_widget(),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'End of day notes, observations, issues...',
            }),
        }
        labels = {
            'opening_photo': 'Report Generator (Main Photo)',
            'closing_photo': 'Shift Report',
        }

from django import forms
from kiosks.models import Kiosk
from .models import SupervisorVisit, BonusPenalty, EVAL_RATING_CHOICES
from accounts.models import User

RATING_WIDGET = lambda: forms.Select(choices=EVAL_RATING_CHOICES, attrs={'class': 'form-select form-select-sm'})
PHOTO_WIDGET  = lambda: forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'accept': 'image/*'})


class VisitForm(forms.ModelForm):
    def __init__(self, *args, supervisor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kiosk'].queryset = Kiosk.objects.filter(is_active=True)

    class Meta:
        model = SupervisorVisit
        fields = [
            'kiosk', 'rating', 'notes',
            'attendance_rating',     'attendance_photo',
            'cleanliness_rating',    'cleanliness_photo',
            'device_care_rating',    'device_care_photo',
            'customer_service_rating', 'customer_service_photo',
            'marketing_rating',      'marketing_photo',
        ]
        widgets = {
            'kiosk': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-select'},
            ),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Visit observations, issues, feedback...',
            }),
            'attendance_rating':       forms.Select(choices=EVAL_RATING_CHOICES, attrs={'class': 'form-select form-select-sm'}),
            'attendance_photo':        forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'accept': 'image/*'}),
            'cleanliness_rating':      forms.Select(choices=EVAL_RATING_CHOICES, attrs={'class': 'form-select form-select-sm'}),
            'cleanliness_photo':       forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'accept': 'image/*'}),
            'device_care_rating':      forms.Select(choices=EVAL_RATING_CHOICES, attrs={'class': 'form-select form-select-sm'}),
            'device_care_photo':       forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'accept': 'image/*'}),
            'customer_service_rating': forms.Select(choices=EVAL_RATING_CHOICES, attrs={'class': 'form-select form-select-sm'}),
            'customer_service_photo':  forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'accept': 'image/*'}),
            'marketing_rating':        forms.Select(choices=EVAL_RATING_CHOICES, attrs={'class': 'form-select form-select-sm'}),
            'marketing_photo':         forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm', 'accept': 'image/*'}),
        }


class BonusPenaltyForm(forms.ModelForm):
    def __init__(self, *args, supervisor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = User.objects.filter(
            role='employee'
        ).order_by('first_name')
        self.fields['employee'].label_from_instance = lambda u: f"{u.get_full_name() or u.username} — {u.kiosk.name if u.kiosk else 'No kiosk'}"

    class Meta:
        model = BonusPenalty
        fields = ['employee', 'type', 'amount', 'reason', 'date']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reason for bonus or penalty...',
            }),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

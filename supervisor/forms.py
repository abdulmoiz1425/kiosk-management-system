from django import forms
from .models import SupervisorVisit, BonusPenalty
from accounts.models import User


class VisitForm(forms.ModelForm):
    class Meta:
        model = SupervisorVisit
        fields = ['kiosk', 'date', 'rating', 'notes']
        widgets = {
            'kiosk': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-select'},
            ),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Visit observations, issues, feedback...',
            }),
        }


class BonusPenaltyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = User.objects.filter(role='employee').order_by('first_name')
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

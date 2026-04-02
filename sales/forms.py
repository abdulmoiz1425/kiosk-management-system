from django import forms
from .models import Sale


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['cash_amount', 'bank_transfer_amount', 'notes']
        widgets = {
            'cash_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
            }),
            'bank_transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes...',
            }),
        }
        labels = {
            'cash_amount': 'Cash Amount (SAR)',
            'bank_transfer_amount': 'Bank Transfer Amount (SAR)',
        }

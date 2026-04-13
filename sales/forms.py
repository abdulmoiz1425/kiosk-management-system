from django import forms
from .models import Sale

_num = lambda ph: forms.NumberInput(attrs={'class': 'form-control', 'placeholder': ph, 'min': '0', 'step': '0.01'})


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'starting_cash', 'cash_amount', 'bank_transfer_amount',
            'actual_cash', 'cashier_photo', 'notes',
        ]
        widgets = {
            'starting_cash':        _num('0.00'),
            'cash_amount':          _num('0.00'),
            'bank_transfer_amount': _num('0.00'),
            'actual_cash':          _num('0.00'),
            'cashier_photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes...',
            }),
        }
        labels = {
            'starting_cash':        'Starting Cash Amount (RM)',
            'cash_amount':          'Cash Payments (RM)',
            'bank_transfer_amount': 'QR Bank Account (RM)',
            'actual_cash':          'Actual Cash Amount (RM)',
            'cashier_photo':        'Cashier Photo',
        }

    def clean_cashier_photo(self):
        photo = self.cleaned_data.get('cashier_photo')
        # Allow existing photo on update (instance already has it)
        if not photo and not (self.instance and self.instance.cashier_photo):
            raise forms.ValidationError('Cashier photo is required.')
        return photo

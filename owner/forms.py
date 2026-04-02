from django import forms
from kiosks.models import Kiosk
from accounts.models import User


class KioskForm(forms.ModelForm):
    class Meta:
        model = Kiosk
        fields = ['name', 'location', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kiosk name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City / mall / area'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full address (optional)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmployeeCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        min_length=6,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'role', 'kiosk', 'assigned_kiosks']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+966...'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'kiosk': forms.Select(attrs={'class': 'form-select'}),
            'assigned_kiosks': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            self.save_m2m()
        return user


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'role', 'kiosk', 'assigned_kiosks', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+966...'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'kiosk': forms.Select(attrs={'class': 'form-select'}),
            'assigned_kiosks': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

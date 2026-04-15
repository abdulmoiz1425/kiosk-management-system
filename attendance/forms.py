from django import forms


class CheckInForm(forms.Form):
    photo = forms.ImageField(
        label='Check-in Photo',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes...'})
    )


class CheckOutForm(forms.Form):
    photo = forms.ImageField(
        label='Check-out Photo',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

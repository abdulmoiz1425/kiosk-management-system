from django import forms
from .models import DailyReport

_photo_widget = lambda: forms.ClearableFileInput(attrs={
    'class': 'form-control',
    'accept': 'image/*',
    'capture': 'environment',
})


class MultipleFileInput(forms.FileInput):
    """FileInput that allows selecting multiple files."""
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        default_attrs = {'multiple': True}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        # data is a list when multiple files selected
        if not data:
            return []
        if not isinstance(data, list):
            data = [data]
        result = []
        for f in data:
            result.append(super().clean(f, initial))
        return result


class DailyReportForm(forms.ModelForm):
    # Extra photos for Report Generator (multiple upload)
    extra_photos = MultipleFileField(
        required=False,
        label='Additional Report Photos',
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
    )

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

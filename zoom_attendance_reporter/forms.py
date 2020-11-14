from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class SmallFilesForm(forms.Form):

    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={
        'multiple': True
    }))

    def __init__(self, *a, **kw):
        """
        Need to override Django's janky behavior with the multiple file
        upload widget.
        """
        self.all_files = kw.pop('all_files', [])
        super().__init__(*a, **kw)

    def clean(self):
        cleaned_data = super().clean()
        for file in self.all_files:
            if file.size > 1e6:  # 1 mb
                raise ValidationError(_('CSV should not be larger than 1mb'), code='invalid')


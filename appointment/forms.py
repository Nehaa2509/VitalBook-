"""
VitalBook — Django Forms
Server-side validation as a safety net behind the JS client-side checks.
"""
import datetime
from django import forms
from .models import Patient


class PatientProfileForm(forms.ModelForm):
    """
    Patient profile update form.
    Max date is intentionally NOT set in Python — JavaScript sets it dynamically
    on every page load so it never goes stale.
    """
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'id': 'dob-input',
            }
        ),
        # Accept all common ISO and locale formats
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'],
    )

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob is None:
            return dob
        today = datetime.date.today()
        if dob > today:
            raise forms.ValidationError('Date of birth cannot be in the future.')
        if dob.year < 1900:
            raise forms.ValidationError('Please enter a valid Date of Birth (year must be 1900 or later).')
        return dob

    class Meta:
        model = Patient
        fields = ['name', 'phone', 'date_of_birth', 'gender', 'blood_group',
                  'address', 'emergency_contact', 'medical_history']

from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .constants import DEPARTMENT_CHOICES, PURPOSE_CHOICES, TIME_SLOT_CHOICES, YEAR_CHOICES
from .models import Appointment, Student


class StudentDetailsForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'registration_number', 'department', 'year', 'email', 'mobile_number']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration number'}),
            'department': forms.Select(attrs={'class': 'form-select'}, choices=DEPARTMENT_CHOICES),
            'year': forms.Select(attrs={'class': 'form-select'}, choices=YEAR_CHOICES),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10 digit mobile number'}),
        }

    def clean_registration_number(self):
        value = (self.cleaned_data.get('registration_number') or '').strip()
        if not value:
            raise ValidationError('Registration number cannot be empty.')
        return value.upper()

    def clean_mobile_number(self):
        value = (self.cleaned_data.get('mobile_number') or '').strip()
        if len(value) != 10 or not value.isdigit():
            raise ValidationError('Mobile number must contain exactly 10 digits.')
        return value


class OtpVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter OTP'}),
        label='Email Verification OTP',
    )


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'purpose', 'appointment_photo', 'additional_notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': date.today().strftime('%Y-%m-%d')}),
            'time': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}, choices=PURPOSE_CHOICES),
            'appointment_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'additional_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Optional notes'}),
        }

    def __init__(self, *args, time_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['purpose'].choices = PURPOSE_CHOICES
        self.fields['time'].choices = time_choices or TIME_SLOT_CHOICES

    def clean_date(self):
        appointment_date = self.cleaned_data['date']
        if appointment_date < date.today():
            raise ValidationError('Past dates cannot be selected.')
        return appointment_date

    def clean_time(self):
        value = self.cleaned_data['time']
        valid_values = {choice[0] for choice in TIME_SLOT_CHOICES}
        if value not in valid_values:
            raise ValidationError('Selected time slot is not available.')
        return value

    def clean_appointment_photo(self):
        photo = self.cleaned_data.get('appointment_photo')
        if photo and photo.size > 5 * 1024 * 1024:
            raise ValidationError('Photo must be 5 MB or smaller.')
        return photo


class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

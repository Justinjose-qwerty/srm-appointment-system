from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .constants import DEPARTMENT_CHOICES, PURPOSE_CHOICES, STATUS_CHOICES, TIME_SLOT_CHOICES, YEAR_CHOICES


class Student(models.Model):
    full_name = models.CharField(max_length=120)
    registration_number = models.CharField(max_length=30, unique=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    year = models.CharField(max_length=10, choices=YEAR_CHOICES)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=10)
    email_otp = models.CharField(max_length=6, blank=True)
    email_otp_sent_at = models.DateTimeField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.full_name} ({self.registration_number})'


class Appointment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    name = models.CharField(max_length=120)
    registration_number = models.CharField(max_length=30, blank=True)
    department = models.CharField(max_length=20, blank=True)
    year = models.CharField(max_length=10, blank=True)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=10, blank=True)
    date = models.DateField()
    time = models.CharField(max_length=5, choices=TIME_SLOT_CHOICES)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    appointment_photo = models.ImageField(upload_to='appointment_photos/', blank=True, null=True)
    additional_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['date', 'time'], name='unique_appointment_slot'),
        ]

    def clean(self):
        if self.date and self.date < timezone.localdate():
            raise ValidationError({'date': 'Past dates are not allowed.'})

        valid_slots = {choice[0] for choice in TIME_SLOT_CHOICES}
        if self.time and self.time not in valid_slots:
            raise ValidationError({'time': 'Selected time is not available.'})

    def __str__(self) -> str:
        return f'{self.name} - {self.date} {self.time}'
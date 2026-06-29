import random

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from .constants import generate_slot_values


def generate_otp(length: int = 6) -> str:
    return ''.join(random.choice('0123456789') for _ in range(length))


def format_time_label(time_value: str) -> str:
    from datetime import datetime
    return datetime.strptime(time_value, '%H:%M').strftime('%I:%M %p')


def get_available_slots_for_date(appointment_model, appointment_date):
    if appointment_date < timezone.localdate():
        return []

    booked_slots = set(
        appointment_model.objects.filter(date=appointment_date).values_list('time', flat=True)
    )

    return [
        {'value': slot, 'label': format_time_label(slot)}
        for slot in generate_slot_values()
        if slot not in booked_slots
    ]


def send_otp_email(recipient_email: str, otp_code: str) -> None:
    subject = 'SRM Student Appointment OTP Verification'
    body = (
        'Your SRM Institute of Science and Technology appointment verification code is '
        f'{otp_code}. This code is valid for 10 minutes.'
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        to=[recipient_email],
    )
    email.send(fail_silently=False)


def is_slot_available(appointment_model, appointment_date, appointment_time) -> bool:
    return not appointment_model.objects.filter(date=appointment_date, time=appointment_time).exists()


def normalize_search_term(value: str) -> str:
    return (value or '').strip()

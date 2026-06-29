from django.test import TestCase
from django.utils import timezone

from .forms import StudentDetailsForm
from .models import Appointment, Student
from .utils import get_available_slots_for_date


class BookingValidationTests(TestCase):
    def test_student_mobile_number_requires_ten_digits(self):
        form = StudentDetailsForm(
            data={
                'full_name': 'Student One',
                'registration_number': 'RA1001',
                'department': 'CSE',
                'year': '1',
                'email': 'student@example.com',
                'mobile_number': '1234',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('mobile_number', form.errors)

    def test_available_slots_excludes_booked_time(self):
        student = Student.objects.create(
            full_name='Student One',
            registration_number='RA1001',
            department='CSE',
            year='1',
            email='student@example.com',
            mobile_number='9876543210',
            email_verified=True,
        )
        target_date = timezone.localdate()
        Appointment.objects.create(
            student=student,
            name=student.full_name,
            registration_number=student.registration_number,
            department=student.department,
            year=student.year,
            email=student.email,
            mobile_number=student.mobile_number,
            date=target_date,
            time='09:00',
            purpose='Academic Discussion',
        )

        slots = get_available_slots_for_date(Appointment, target_date)
        self.assertTrue(all(slot['value'] != '09:00' for slot in slots))
from django.test import TestCase

# Create your tests here.

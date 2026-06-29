from datetime import datetime

from django.contrib import messages
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .constants import STATUS_CHOICES
from .decorators import srm_admin_required
from .forms import AdminLoginForm, AppointmentForm, OtpVerificationForm, StudentDetailsForm
from .models import Appointment, Student
from .utils import generate_otp, get_available_slots_for_date, is_slot_available, send_otp_email


ADMIN_USERNAME = getattr(settings, 'ADMIN_USERNAME', 'srmadmin')
ADMIN_PASSWORD = getattr(settings, 'ADMIN_PASSWORD', 'change-me')


def student_booking(request):
    """Main public booking page with a two-step student appointment flow."""
    student_id = request.session.get('student_draft_id')
    student = Student.objects.filter(id=student_id).first() if student_id else None
    student_form = StudentDetailsForm(instance=student)
    otp_form = OtpVerificationForm()
    appointment_form = None
    available_slots = []

    if student and student.email_verified:
        appointment_form = AppointmentForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_student':
            student_form = StudentDetailsForm(request.POST, instance=student)
            otp_form = OtpVerificationForm()

            if student_form.is_valid():
                student_instance = student_form.save(commit=False)
                student_instance.email_verified = False
                otp_code = generate_otp()
                student_instance.email_otp = otp_code
                student_instance.email_otp_sent_at = timezone.now()
                student_instance.save()
                request.session['student_draft_id'] = student_instance.id
                request.session['otp_email'] = student_instance.email

                try:
                    send_otp_email(student_instance.email, otp_code)
                    messages.success(request, f'Verification code sent to {student_instance.email}.')
                except Exception as exc:
                    messages.error(request, f'Unable to send verification email: {exc}')

                student = student_instance
            else:
                messages.error(request, 'Please correct the student details before continuing.')

        elif action == 'verify_otp':
            student = Student.objects.filter(id=request.session.get('student_draft_id')).first()
            if not student:
                messages.error(request, 'Please submit student details first.')
            else:
                otp_form = OtpVerificationForm(request.POST)
                if otp_form.is_valid():
                    entered_otp = otp_form.cleaned_data['otp'].strip()
                    otp_age = timezone.now() - (student.email_otp_sent_at or timezone.now())
                    if otp_age.total_seconds() > 600:
                        messages.error(request, 'OTP expired. Please resend verification.')
                    elif entered_otp == student.email_otp:
                        student.email_verified = True
                        student.email_otp = ''
                        student.save(update_fields=['email_verified', 'email_otp', 'updated_at'])
                        messages.success(request, 'Email verified successfully. You can continue to appointment details.')
                    else:
                        messages.error(request, 'Invalid OTP. Please try again.')

        elif action == 'book_appointment':
            student = Student.objects.filter(id=request.session.get('student_draft_id'), email_verified=True).first()
            if not student:
                messages.error(request, 'Verify your email before booking an appointment.')
            else:
                appointment_form = AppointmentForm(request.POST, request.FILES)
                if appointment_form.is_valid():
                    appointment_date = appointment_form.cleaned_data['date']
                    appointment_time = appointment_form.cleaned_data['time']

                    if not is_slot_available(Appointment, appointment_date, appointment_time):
                        appointment_form.add_error('time', 'This slot has already been booked.')
                    else:
                        try:
                            with transaction.atomic():
                                appointment = appointment_form.save(commit=False)
                                appointment.student = student
                                appointment.name = student.full_name
                                appointment.registration_number = student.registration_number
                                appointment.department = student.department
                                appointment.year = student.year
                                appointment.email = student.email
                                appointment.mobile_number = student.mobile_number
                                appointment.status = 'Pending'
                                appointment.save()

                            messages.success(request, 'Appointment Submitted Successfully.')
                            request.session.pop('student_draft_id', None)
                            request.session.pop('otp_email', None)
                            return redirect('student_booking')
                        except IntegrityError:
                            appointment_form.add_error('time', 'This slot has already been booked.')

        elif action == 'resend_otp':
            student = Student.objects.filter(id=request.session.get('student_draft_id')).first()
            if student:
                otp_code = generate_otp()
                student.email_otp = otp_code
                student.email_verified = False
                student.email_otp_sent_at = timezone.now()
                student.save(update_fields=['email_otp', 'email_verified', 'email_otp_sent_at', 'updated_at'])
                try:
                    send_otp_email(student.email, otp_code)
                    messages.success(request, f'A new verification code has been sent to {student.email}.')
                except Exception as exc:
                    messages.error(request, f'Unable to resend OTP right now: {exc}')

    if student and student.email_verified:
        appointment_form = appointment_form or AppointmentForm()
        if appointment_form.is_bound and appointment_form.data.get('date'):
            try:
                selected_date = datetime.strptime(appointment_form.data['date'], '%Y-%m-%d').date()
                available_slots = get_available_slots_for_date(Appointment, selected_date)
                appointment_form.fields['time'].choices = [(slot['value'], slot['label']) for slot in available_slots]
            except ValueError:
                available_slots = []

    return render(
        request,
        'student_booking.html',
        {
            'student_form': student_form,
            'otp_form': otp_form,
            'appointment_form': appointment_form,
            'student': student,
            'available_slots': available_slots,
            'email_delivery_ready': bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD),
            'email_backend_name': settings.EMAIL_BACKEND.rsplit('.', 1)[-1],
        },
    )


def book_appointment(request):
    """Backward-compatible alias for the original booking route."""
    return student_booking(request)


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                request.session['srm_admin_authenticated'] = True
                request.session['srm_admin_username'] = username
                messages.success(request, 'Welcome to the SRM Admin Dashboard.')
                return redirect('admin_dashboard')
            messages.error(request, 'Invalid Username or Password')
    else:
        form = AdminLoginForm()

    return render(request, 'admin_login.html', {'form': form})


@srm_admin_required
def admin_dashboard(request):
    search = (request.GET.get('search') or '').strip()
    status_filter = (request.GET.get('status') or '').strip()
    date_filter = (request.GET.get('date') or '').strip()
    sort_order = request.GET.get('sort', 'newest')

    appointments = Appointment.objects.select_related('student').all()

    if search:
        appointments = appointments.filter(
            Q(name__icontains=search) | Q(registration_number__icontains=search)
        )

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    if date_filter:
        appointments = appointments.filter(date=date_filter)

    if sort_order == 'oldest':
        appointments = appointments.order_by('created_at')
    else:
        appointments = appointments.order_by('-created_at')

    total_appointments = Appointment.objects.count()
    summary = {
        'total': total_appointments,
        'pending': Appointment.objects.filter(status='Pending').count(),
        'accepted': Appointment.objects.filter(status='Accepted').count(),
        'rejected': Appointment.objects.filter(status='Rejected').count(),
        'completed': Appointment.objects.filter(status='Completed').count(),
        'today': Appointment.objects.filter(date=timezone.localdate()).count(),
    }

    status_counts = Appointment.objects.values('status').annotate(count=Count('id'))
    status_map = {item['status']: item['count'] for item in status_counts}

    return render(
        request,
        'admin_dashboard.html',
        {
            'appointments': appointments,
            'summary': summary,
            'status_map': status_map,
            'status_choices': STATUS_CHOICES,
            'filters': {
                'search': search,
                'status': status_filter,
                'date': date_filter,
                'sort': sort_order,
            },
        },
    )


@srm_admin_required
@require_POST
def appointment_action(request, appointment_id, action):
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    if action == 'accept':
        appointment.status = 'Accepted'
        appointment.rejection_reason = ''
        appointment.save(update_fields=['status', 'rejection_reason', 'updated_at'])
        messages.success(request, 'Appointment accepted.')
    elif action == 'complete':
        appointment.status = 'Completed'
        appointment.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Appointment marked as completed.')
    elif action == 'reject':
        rejection_reason = (request.POST.get('rejection_reason') or '').strip()
        if not rejection_reason:
            messages.error(request, 'A rejection reason is required.')
        else:
            appointment.status = 'Rejected'
            appointment.rejection_reason = rejection_reason
            appointment.save(update_fields=['status', 'rejection_reason', 'updated_at'])
            messages.success(request, 'Appointment rejected.')
    else:
        raise Http404()

    return redirect('admin_dashboard')


@srm_admin_required
def admin_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('admin_login')


@srm_admin_required
def admin_stats(request):
    data = {
        'total': Appointment.objects.count(),
        'pending': Appointment.objects.filter(status='Pending').count(),
        'accepted': Appointment.objects.filter(status='Accepted').count(),
        'rejected': Appointment.objects.filter(status='Rejected').count(),
        'completed': Appointment.objects.filter(status='Completed').count(),
        'today': Appointment.objects.filter(date=timezone.localdate()).count(),
    }
    return JsonResponse(data)


def available_slots(request):
    date_value = (request.GET.get('date') or '').strip()
    if not date_value:
        return JsonResponse({'slots': []})

    try:
        appointment_date = datetime.strptime(date_value, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'slots': []}, status=400)

    slots = get_available_slots_for_date(Appointment, appointment_date)
    return JsonResponse({'slots': slots})

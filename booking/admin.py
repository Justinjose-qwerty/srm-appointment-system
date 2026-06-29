from django.contrib import admin

from .models import Appointment, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'registration_number', 'department', 'year', 'email', 'email_verified')
    list_filter = ('department', 'year', 'email_verified')
    search_fields = ('full_name', 'registration_number', 'email')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'email', 'date', 'time', 'purpose', 'status')
    list_filter = ('status', 'purpose', 'date')
    search_fields = ('name', 'registration_number', 'email')
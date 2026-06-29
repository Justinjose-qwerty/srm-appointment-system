from datetime import datetime

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def normalize_existing_time_values(apps, schema_editor):
    Appointment = apps.get_model('booking', 'Appointment')
    for appointment in Appointment.objects.all():
        value = appointment.time
        if hasattr(value, 'strftime'):
            appointment.time = value.strftime('%H:%M')
        elif isinstance(value, str):
            try:
                parsed = datetime.strptime(value, '%H:%M:%S').strftime('%H:%M')
            except ValueError:
                try:
                    parsed = datetime.strptime(value, '%H:%M').strftime('%H:%M')
                except ValueError:
                    parsed = '09:00'
            appointment.time = parsed
        else:
            appointment.time = '09:00'
        appointment.save(update_fields=['time'])


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=120)),
                ('registration_number', models.CharField(max_length=30, unique=True)),
                ('department', models.CharField(choices=[('CSE', 'Computer Science and Engineering'), ('ECE', 'Electronics and Communication Engineering'), ('EEE', 'Electrical and Electronics Engineering'), ('MECH', 'Mechanical Engineering'), ('CIVIL', 'Civil Engineering'), ('IT', 'Information Technology'), ('MBA', 'Master of Business Administration'), ('BBA', 'Bachelor of Business Administration'), ('OTHER', 'Other')], max_length=20)),
                ('year', models.CharField(choices=[('1', 'First Year'), ('2', 'Second Year'), ('3', 'Third Year'), ('4', 'Fourth Year'), ('PG', 'Post Graduate')], max_length=10)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('mobile_number', models.CharField(max_length=10)),
                ('email_otp', models.CharField(blank=True, max_length=6)),
                ('email_otp_sent_at', models.DateTimeField(blank=True, null=True)),
                ('email_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('updated_at', models.DateTimeField(default=timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments', to='booking.student'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='registration_number',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='appointment',
            name='department',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='appointment',
            name='year',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='appointment',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='appointment',
            name='additional_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='name',
            field=models.CharField(max_length=120),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='time',
            field=models.CharField(choices=[('09:00', '09:00 AM'), ('09:30', '09:30 AM'), ('10:00', '10:00 AM'), ('10:30', '10:30 AM'), ('11:00', '11:00 AM'), ('11:30', '11:30 AM')], max_length=5),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='purpose',
            field=models.CharField(choices=[('Academic Discussion', 'Academic Discussion'), ('Project Discussion', 'Project Discussion'), ('Internship Discussion', 'Internship Discussion'), ('Faculty Consultation', 'Faculty Consultation'), ('Research Discussion', 'Research Discussion'), ('Leave Approval', 'Leave Approval'), ('Other', 'Other')], max_length=50),
        ),
        migrations.AddField(
            model_name='appointment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.RunPython(normalize_existing_time_values, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='appointment',
            constraint=models.UniqueConstraint(fields=('date', 'time'), name='unique_appointment_slot'),
        ),
        migrations.AlterModelOptions(
            name='appointment',
            options={'ordering': ['-created_at']},
        ),
    ]

from datetime import datetime, time, timedelta

DEPARTMENT_CHOICES = [
    ('CSE', 'Computer Science and Engineering'),
    ('ECE', 'Electronics and Communication Engineering'),
    ('EEE', 'Electrical and Electronics Engineering'),
    ('MECH', 'Mechanical Engineering'),
    ('CIVIL', 'Civil Engineering'),
    ('IT', 'Information Technology'),
    ('MBA', 'Master of Business Administration'),
    ('BBA', 'Bachelor of Business Administration'),
    ('OTHER', 'Other'),
]

YEAR_CHOICES = [
    ('1', 'First Year'),
    ('2', 'Second Year'),
    ('3', 'Third Year'),
    ('4', 'Fourth Year'),
    ('PG', 'Post Graduate'),
]

PURPOSE_CHOICES = [
    ('Academic Discussion', 'Academic Discussion'),
    ('Project Discussion', 'Project Discussion'),
    ('Internship Discussion', 'Internship Discussion'),
    ('Faculty Consultation', 'Faculty Consultation'),
    ('Research Discussion', 'Research Discussion'),
    ('Leave Approval', 'Leave Approval'),
    ('Other', 'Other'),
]

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected'),
    ('Completed', 'Completed'),
]

OFFICE_START_TIME = time(9, 0)
OFFICE_END_TIME = time(12, 0)
SLOT_DURATION_MINUTES = 30


def generate_slot_values():
    """Return the six office-hour appointment slots for the day."""
    slots = []
    current = datetime.combine(datetime.today(), OFFICE_START_TIME)
    end_time = datetime.combine(datetime.today(), OFFICE_END_TIME)

    while current < end_time:
        slots.append(current.strftime('%H:%M'))
        current += timedelta(minutes=SLOT_DURATION_MINUTES)

    return slots


TIME_SLOT_CHOICES = [(slot, datetime.strptime(slot, '%H:%M').strftime('%I:%M %p')) for slot in generate_slot_values()]

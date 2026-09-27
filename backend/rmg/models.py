from django.contrib.auth.models import User
from django.db import models


class Associate(models.Model):
    AVAILABILITY_CHOICES = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]
    ALLOCATION_CHOICES = [
        ('Unallocated', 'Unallocated'),
        ('Interviewing', 'Interviewing'),
        ('Allocated', 'Allocated'),
    ]

    employee_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    experience = models.IntegerField(default=0)
    skills = models.TextField(help_text='Comma-separated skills')
    location = models.CharField(max_length=100)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='Available')
    allocation_status = models.CharField(max_length=20, choices=ALLOCATION_CHOICES, default='Unallocated')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='associate_profile')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.employee_id})'


class Project(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    ]

    project_name = models.CharField(max_length=200)
    client = models.CharField(max_length=200)
    required_skills = models.TextField(help_text='Comma-separated skills')
    minimum_experience = models.IntegerField(default=0)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.project_name


class Interview(models.Model):
    INTERVIEW_TYPE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
    ]
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
        ('On Hold', 'On Hold'),
    ]

    associate = models.ForeignKey(Associate, on_delete=models.CASCADE, related_name='interviews')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='interviews')
    interview_date = models.DateField()
    interview_time = models.TimeField()
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.associate.name} - {self.project.project_name}'

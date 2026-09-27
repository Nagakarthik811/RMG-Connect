from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from rmg.models import Associate, Project


class Command(BaseCommand):
    help = 'Create or refresh the RMG Connect demonstration accounts and records.'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@tcs.com', 'is_staff': True})
        admin.is_staff = True
        admin.set_password('Admin123!')
        admin.save()
        examples = [
            ('TCS1001', 'Rahul Sharma', 'rahul@tcs.com', '9876543210', 2, 'Python, SQL, Django', 'Bangalore', 'rahul'),
            ('TCS1002', 'Ravi Kumar', 'ravi@tcs.com', '9876543211', 3, 'Java, SQL, Spring Boot', 'Hyderabad', 'ravi'),
            ('TCS1003', 'Priya Reddy', 'priya@tcs.com', '9876543212', 2, 'React, JavaScript, HTML, CSS', 'Chennai', 'priya'),
        ]
        for emp, name, email, phone, exp, skills, location, username in examples:
            user, _ = User.objects.get_or_create(username=username, defaults={'email': email})
            user.email = email
            user.set_password('Associate123!')
            user.save()
            Associate.objects.update_or_create(employee_id=emp, defaults={
                'name': name, 'email': email, 'phone': phone, 'experience': exp,
                'skills': skills, 'location': location, 'availability_status': 'Available',
                'allocation_status': 'Unallocated', 'user': user,
            })
        projects = [
            ('Python Backend Developer', 'Internal Banking Project', 'Python, Django, SQL', 2, 'Bangalore', 'Backend development and maintenance'),
            ('Java Backend Developer', 'Digital Platforms', 'Java, Spring Boot, SQL', 2, 'Hyderabad', 'Build and maintain backend services'),
            ('Frontend Developer', 'Customer Experience', 'React, JavaScript, HTML, CSS', 1, 'Chennai', 'Develop responsive web interfaces'),
        ]
        for name, client, skills, exp, location, description in projects:
            Project.objects.get_or_create(project_name=name, defaults={
                'client': client, 'required_skills': skills, 'minimum_experience': exp,
                'location': location, 'description': description, 'status': 'Open',
            })
        self.stdout.write(self.style.SUCCESS('Demo data ready. Admin: admin / Admin123!; associates: rahul, ravi, priya / Associate123!'))

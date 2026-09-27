import os
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Associate, Interview, Project


class RMGWorkflowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('workflow-admin', password='AdminPass123!', is_staff=True)
        self.admin_client = APIClient(enforce_csrf_checks=True)
        response = self.admin_client.post('/api/login/', {'username': 'workflow-admin', 'password': 'AdminPass123!'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.admin_csrf = self.admin_client.cookies['csrftoken'].value

    def test_admin_to_associate_allocation_workflow(self):
        project_response = self.admin_client.post('/api/projects/', {
            'project_name': 'Workflow Python Project', 'client': 'Internal Banking',
            'required_skills': 'Python, Django, SQL', 'minimum_experience': 2,
            'location': 'Bangalore', 'description': 'Test workflow project', 'status': 'Open',
        }, format='json', HTTP_X_CSRFTOKEN=self.admin_csrf)
        self.assertEqual(project_response.status_code, 201, project_response.data)
        project_id = project_response.data['id']

        associate_response = self.admin_client.post('/api/associates/', {
            'employee_id': 'TCS9001', 'name': 'Workflow Rahul', 'email': 'workflow-rahul@tcs.com',
            'phone': '9000000001', 'experience': 2, 'skills': 'Python, SQL, Django',
            'location': 'Bangalore', 'availability_status': 'Available', 'allocation_status': 'Unallocated',
        }, format='json', HTTP_X_CSRFTOKEN=self.admin_csrf)
        self.assertEqual(associate_response.status_code, 201, associate_response.data)
        associate_id = associate_response.data['id']
        associate = Associate.objects.get(pk=associate_id)
        self.assertEqual(associate.user.username, 'tcs9001')
        self.assertTrue(associate.user.check_password('Welcome123!'))

        matches = self.admin_client.get(f'/api/projects/{project_id}/matches/')
        self.assertEqual(matches.status_code, 200, matches.data)
        self.assertEqual(matches.data[0]['id'], associate_id)
        self.assertEqual(matches.data[0]['matching_skills'], 3)
        self.assertEqual(matches.data[0]['match_percentage'], 100)

        interview_response = self.admin_client.post('/api/interviews/', {
            'associate_id': associate_id, 'project_id': project_id,
            'interview_date': '2030-09-30', 'interview_time': '11:00',
            'interview_type': 'Online', 'status': 'Scheduled', 'remarks': 'Workflow test call',
        }, format='json', HTTP_X_CSRFTOKEN=self.admin_csrf)
        self.assertEqual(interview_response.status_code, 201, interview_response.data)
        interview_id = interview_response.data['id']
        associate.refresh_from_db()
        self.assertEqual(associate.allocation_status, 'Interviewing')

        associate_client = APIClient(enforce_csrf_checks=True)
        associate_login = associate_client.post('/api/login/', {
            'username': 'tcs9001', 'password': 'Welcome123!',
        }, format='json')
        self.assertEqual(associate_login.status_code, 200, associate_login.data)
        self.assertEqual(associate_login.data['role'], 'associate')
        self.assertEqual(associate_client.get('/api/my-profile/').data['employee_id'], 'TCS9001')
        self.assertEqual(len(associate_client.get('/api/my-interviews/').data), 1)
        self.assertEqual(len(associate_client.get('/api/my-opportunities/').data), 0)

        update = self.admin_client.patch(f'/api/interviews/{interview_id}/', {'status': 'Selected'}, format='json', HTTP_X_CSRFTOKEN=self.admin_csrf)
        self.assertEqual(update.status_code, 200, update.data)
        self.assertEqual(update.data['status'], 'Selected')
        allocated = self.admin_client.post(f'/api/interviews/{interview_id}/allocate/', {}, format='json', HTTP_X_CSRFTOKEN=self.admin_csrf)
        self.assertEqual(allocated.status_code, 200, allocated.data)
        associate.refresh_from_db()
        self.assertEqual(associate.allocation_status, 'Allocated')
        self.assertEqual(self.admin_client.get(f'/api/projects/{project_id}/matches/').data, [])
        self.assertEqual(Interview.objects.get(pk=interview_id).status, 'Selected')

    def test_invalid_login_and_admin_only_mutations(self):
        anon = APIClient()
        bad_login = anon.post('/api/login/', {'username': 'unknown', 'password': 'bad'}, format='json')
        self.assertEqual(bad_login.status_code, 400)
        self.assertEqual(anon.get('/api/associates/').status_code, 403)
        self.assertEqual(self.admin_client.get('/api/associates/').status_code, 200)

    def test_bootstrap_admin_creates_superuser_only_once(self):
        environment = {
            'DJANGO_SUPERUSER_USERNAME': 'deployed-admin',
            'DJANGO_SUPERUSER_EMAIL': 'deployed-admin@example.com',
            'DJANGO_SUPERUSER_PASSWORD': 'StrongDeployPassword123!',
        }
        with patch.dict(os.environ, environment):
            call_command('bootstrap_admin')
            admin = User.objects.get(username='deployed-admin')
            self.assertTrue(admin.is_superuser)
            self.assertTrue(admin.check_password(environment['DJANGO_SUPERUSER_PASSWORD']))

            admin.set_password('ChangedPassword456!')
            admin.save()
            call_command('bootstrap_admin')
            admin.refresh_from_db()
            self.assertTrue(admin.check_password('ChangedPassword456!'))

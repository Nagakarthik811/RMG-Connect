from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Associate, Interview, Project
from .serializers import (
    AssociateCreateSerializer,
    AssociateSerializer,
    InterviewSerializer,
    LoginSerializer,
    ProjectCreateSerializer,
    ProjectSerializer,
)


class IsRMGAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        is_admin = user.is_staff or user.is_superuser
        role = 'admin' if is_admin else 'associate'
        data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
            },
            'role': role,
            'message': 'Login successful'
        }
        return Response(data, status=status.HTTP_200_OK)
    return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out.'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_summary(request):
    total_associates = Associate.objects.count()
    unallocated_associates = Associate.objects.filter(allocation_status='Unallocated').count()
    open_projects = Project.objects.filter(status='Open').count()
    scheduled_interviews = Interview.objects.filter(status='Scheduled').count()
    selected_associates = Interview.objects.filter(status='Selected').values('associate_id').distinct().count()

    return Response({
        'total_associates': total_associates,
        'unallocated_associates': unallocated_associates,
        'open_projects': open_projects,
        'scheduled_interviews': scheduled_interviews,
        'selected_associates': selected_associates,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_profile(request):
    user = request.user
    associate = Associate.objects.filter(user=user).first()
    if not associate:
        return Response({'error': 'Associate profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(AssociateSerializer(associate).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_opportunities(request):
    user = request.user
    associate = Associate.objects.filter(user=user).first()
    if not associate or associate.availability_status != 'Available' or associate.allocation_status != 'Unallocated':
        return Response([], status=status.HTTP_200_OK)

    projects = []
    for project in Project.objects.filter(status='Open'):
        required = [item.strip() for item in project.required_skills.split(',') if item.strip()]
        associate_skills = [item.strip() for item in associate.skills.split(',') if item.strip()]
        matches = {skill.casefold() for skill in required}.intersection(skill.casefold() for skill in associate_skills)
        percent = (len(matches) / len(required) * 100) if required else 0
        if associate.experience >= project.minimum_experience and percent >= 50:
            projects.append({
                'id': project.id,
                'project_name': project.project_name,
                'required_skills': project.required_skills,
                'location': project.location,
                'minimum_experience': project.minimum_experience,
                'status': project.status,
                'match_percentage': round(percent, 2),
            })
    return Response(projects)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_interviews(request):
    user = request.user
    associate = Associate.objects.filter(user=user).first()
    if not associate:
        return Response([], status=status.HTTP_200_OK)
    interviews = Interview.objects.filter(associate=associate)
    serializer = InterviewSerializer(interviews, many=True)
    return Response(serializer.data)


class AssociateViewSet(viewsets.ModelViewSet):
    queryset = Associate.objects.all()
    serializer_class = AssociateSerializer
    permission_classes = [IsRMGAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return AssociateCreateSerializer
        return AssociateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name = request.query_params.get('name', '').strip()
        employee_id = request.query_params.get('employee_id', '').strip()
        skill = request.query_params.get('skill', '').strip()
        allocation = request.query_params.get('allocation_status', '').strip()

        if name and employee_id:
            queryset = queryset.filter(Q(name__icontains=name) | Q(employee_id__icontains=employee_id))
        elif name:
            queryset = queryset.filter(name__icontains=name)
        elif employee_id:
            queryset = queryset.filter(employee_id__icontains=employee_id)
        if skill:
            queryset = queryset.filter(skills__icontains=skill)
        if allocation:
            queryset = queryset.filter(allocation_status=allocation)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        if user:
            user.delete()


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsRMGAdmin]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateSerializer
        return ProjectSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name = request.query_params.get('name', '').strip()
        status_param = request.query_params.get('status', '').strip()

        if name:
            queryset = queryset.filter(project_name__icontains=name)
        if status_param:
            queryset = queryset.filter(status=status_param)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [IsRMGAdmin]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        status_param = request.query_params.get('status', '').strip()
        if status_param:
            queryset = queryset.filter(status=status_param)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        interview = serializer.save()
        associate = interview.associate
        if associate.availability_status != 'Available' or associate.allocation_status != 'Unallocated':
            interview.delete()
            return Response({'error': 'Only available, unallocated associates can be interviewed.'}, status=status.HTTP_400_BAD_REQUEST)
        associate.allocation_status = 'Interviewing'
        associate.save()
        return Response(self.get_serializer(interview).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        interview = serializer.save()

        if interview.status == 'Selected':
            interview.associate.allocation_status = 'Interviewing'
            interview.associate.save()

        if interview.status in ['Rejected', 'On Hold']:
            interview.associate.allocation_status = 'Unallocated'
            interview.associate.save()

        return Response(self.get_serializer(interview).data)


@api_view(['GET'])
@permission_classes([IsRMGAdmin])
def project_matches(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    required_skills = [item.strip() for item in project.required_skills.split(',') if item.strip()]
    if not required_skills:
        return Response([])

    candidates = []
    for associate in Associate.objects.filter(availability_status='Available', allocation_status='Unallocated'):
        if associate.experience < project.minimum_experience:
            continue
        associate_skills = [item.strip() for item in associate.skills.split(',') if item.strip()]
        matched = {skill.casefold() for skill in required_skills}.intersection(skill.casefold() for skill in associate_skills)
        match_count = len(matched)
        percentage = round((match_count / len(required_skills)) * 100, 2) if required_skills else 0

        if percentage >= 50:
            candidates.append({
                'id': associate.id,
                'employee_id': associate.employee_id,
                'name': associate.name,
                'skills': associate.skills,
                'experience': associate.experience,
                'location': associate.location,
                'availability_status': associate.availability_status,
                'allocation_status': associate.allocation_status,
                'matching_skills': match_count,
                'match_percentage': percentage,
                'total_required_skills': len(required_skills),
            })

    return Response(candidates)


@api_view(['POST'])
@permission_classes([IsRMGAdmin])
def allocate_associate_to_project(request, interview_id):
    try:
        interview = Interview.objects.get(pk=interview_id)
    except Interview.DoesNotExist:
        return Response({'error': 'Interview not found.'}, status=status.HTTP_404_NOT_FOUND)

    if interview.status != 'Selected':
        return Response({'error': 'Only selected interviews can be allocated.'}, status=status.HTTP_400_BAD_REQUEST)

    associate = interview.associate
    if associate.allocation_status == 'Allocated':
        return Response({'error': 'Associate is already allocated.'}, status=status.HTTP_400_BAD_REQUEST)
    associate.allocation_status = 'Allocated'
    associate.availability_status = 'Available'
    associate.save()

    interview.remarks = 'Allocated to project'
    interview.save()

    return Response({'message': 'Associate allocated successfully.', 'associate_id': associate.id})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    data = {
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
    }
    return Response(data)

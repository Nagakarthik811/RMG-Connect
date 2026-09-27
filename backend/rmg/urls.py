from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssociateViewSet,
    InterviewViewSet,
    ProjectViewSet,
    allocate_associate_to_project,
    current_user,
    dashboard_summary,
    login_view,
    logout_view,
    my_interviews,
    my_opportunities,
    my_profile,
    project_matches,
)

router = DefaultRouter()
router.register(r'associates', AssociateViewSet, basename='associate')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'interviews', InterviewViewSet, basename='interview')

urlpatterns = [
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('api/dashboard-summary/', dashboard_summary, name='dashboard-summary'),
    path('api/me/', current_user, name='current-user'),
    path('api/my-profile/', my_profile, name='my-profile'),
    path('api/my-opportunities/', my_opportunities, name='my-opportunities'),
    path('api/my-interviews/', my_interviews, name='my-interviews'),
    path('api/projects/<int:project_id>/matches/', project_matches, name='project-matches'),
    path('api/interviews/<int:interview_id>/allocate/', allocate_associate_to_project, name='allocate-associate'),
]

urlpatterns += [path('api/', include(router.urls))]

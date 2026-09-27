from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rmg.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
    re_path(r'^(?!api/|admin/|static/).+$', TemplateView.as_view(template_name='index.html')),
]

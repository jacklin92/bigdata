    
from django.urls import path
from django.views.generic import TemplateView   

app_name="app_poa_introduction"

urlpatterns = [
    # course introduction
    path('course_intro', TemplateView.as_view(template_name='app_poa_introduction/course-introduction.html'), name='course_introduction'),

    # api introduction
    path('api_intro', TemplateView.as_view(template_name='app_poa_introduction/api-introduction.html'), name='api_introduction'),
]


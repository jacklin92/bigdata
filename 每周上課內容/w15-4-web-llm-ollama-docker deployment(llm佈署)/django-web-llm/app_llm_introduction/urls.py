    
from django.urls import path
from django.views.generic import TemplateView   
from . import views

app_name="app_llm_introduction"

urlpatterns = [
    # LLM introduction
    path('llm-introduction/', TemplateView.as_view(template_name='app_llm_introduction/llm-introduction.html'), name='llm_introduction'),

    # Model Introduction
    path('model-introduction/', views.model_introduction, name='model_introduction'),
]


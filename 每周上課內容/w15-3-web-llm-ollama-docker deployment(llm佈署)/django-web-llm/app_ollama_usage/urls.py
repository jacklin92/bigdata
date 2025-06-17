from django.urls import path
from . import views

app_name = 'app_ollama_usage'

urlpatterns = [
    # 直接進入這個網頁
    path('', views.home, name='home'),
    path('api_ollama_chat/', views.api_ollama_chat, name='api_ollama_chat'),
    
]

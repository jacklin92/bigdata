from django.urls import path
from app_person_volume import views

app_name='app_person_volume'

urlpatterns = [
    path('', views.home, name='home'),
    path('api_get_taipei_mayor_data/', views.api_get_taipei_mayor_data),
]

from django.urls import path
from app_taipei_mayor import views

app_name='namespace_taipei_mayor'

urlpatterns = [
    path('', views.home, name='home'),
    path('api_get_taipei_mayor_data/', views.api_get_taipei_mayor_data),
]

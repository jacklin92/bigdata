from django.urls import path
from app_person_fan import views

# Declare a namespace for this APP
app_name = "app_person_fan"

urlpatterns = [
    # top (popular) persons
    path('', views.home, name='home'),
]
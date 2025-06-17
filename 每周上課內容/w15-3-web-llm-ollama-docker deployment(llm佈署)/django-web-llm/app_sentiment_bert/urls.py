from django.urls import path
from . import views

app_name = 'app_sentiment_bert'

urlpatterns = [
    path('', views.home, name='home'),
    path('api_get_sentiment/', views.api_get_sentiment),
]

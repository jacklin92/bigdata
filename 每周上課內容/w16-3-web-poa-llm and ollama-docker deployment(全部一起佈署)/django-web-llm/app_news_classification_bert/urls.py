from django.urls import path
from . import views

app_name = 'app_news_classification_bert'

urlpatterns = [
    path('', views.home, name='home'),
    path('api_get_news_category/', views.api_get_news_category),
]

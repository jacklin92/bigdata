from django.urls import path
from app_top_keyword import views

# Declare a namespace for this APP
app_name = "app_top_keyword"

urlpatterns = [
    # For home
    path("", views.home, name="home"),
    path("topword/", views.api_get_cate_topword, name="api_cate_topword"),
    # For Ajax
    path('api_get_cate_topword/', views.api_get_cate_topword),
]

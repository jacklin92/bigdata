from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # app top keywords
    # path('', include('app_top_keyword.urls')), # root path
    path("topword/", include("app_top_keyword.urls")),
    # app top persons
    path("topperson/", include("app_top_person.urls")),
]

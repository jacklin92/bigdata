from django.urls import path
from django.urls import include

urlpatterns = [
    # top keywords
    path("topword/", include("app_top_keyword.urls")),
    # top persons
    path("topperson/", include("app_top_person.urls")),
    # top name entity keyword
    # path('topner/', include('app_top_ner.urls')),
    # user keyword analysis
    path("userkeyword/", include("app_user_keyword.urls")),
    path("personfan/", include("app_person_fan.urls")),
]

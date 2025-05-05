from django.contrib import admin
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
    path("userkeyword_assoc/", include("app_user_keyword_association.urls")),
    # user keyword sentiment
    path("userkeyword_senti/", include("app_user_keyword_sentiment.urls")),
    path("taipeimayor/", include("app_taipei_mayor.urls")),
    path('userkeyword_db/', include('app_user_keyword_db.urls')),
    # admin
    path('admin/', admin.site.urls),
    path('topperson_db/', include('app_top_person_db.urls')),

]

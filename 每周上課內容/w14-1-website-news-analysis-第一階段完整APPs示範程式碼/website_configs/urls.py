from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    # top keywords
    path('topword/', include('app_top_keyword.urls')),
    
    # app top persons
    path('topperson/', include('app_top_person.urls')),
    # top ner
    path('topner/', include('app_top_ner.urls')),
    # user keyword analysis
    path('userkeyword/', include('app_user_keyword.urls')),
    
    # app shih chung chen
    path('scchen/', include('app_scchen.urls')),
    
    # app who is the most popular yesterday
    # path('toppersonYesterday/', include('app_top_person_yesterday.urls')),
   
    # full text search and associated keyword display
    path('userkeyword_assoc/', include('app_user_keyword_association.urls')),
    
    # user keyword sentiment 
    path('userkeyword_senti/', include('app_user_keyword_sentiment.urls')),
    
    # user keyword sentiment 
    path('userkeyword_report/', include('app_user_keyword_llm_report.urls')),
    
    # taipei mayor election
    # path('taipeimayor/', include('app_taipei_mayor.urls')),

    # taipei mayor election
    path('', include('app_taipei_mayor.urls')),
    
    # correlation
    path('correlation/', include('app_correlation_analysis.urls')),

    # top k person using db
    path('topperson_db/', include('app_top_person_db.urls')),
    
    # top k person using db
    path('topperson_sqlalchemy_db/', include('app_top_person_sqlalchemy_db.urls')),
    
    # full text search and associated keyword display using db
    path('userkeyword_db/', include('app_user_keyword_db.urls')),

    # admin
    path('admin/', admin.site.urls),
    
    
    # course introduction
    # path('', include('app_poa_introduction.urls')),
    path('poa_intro/', include('app_poa_introduction.urls')),
    
    # Sentiment classification with bert
    #path('sentiment/', include('app_sentiment_bert.urls')),

    # News classification
    #path('news_cls/', include('app_news_classification_bert.urls')),
    
    
    # news recommendation with bert
    #path('news_rcmd/', include('app_news_rcmd_bert.urls')),

    
]

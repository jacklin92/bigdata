from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    # llm and classifier: 
    # sentiment analysis, news classification and qwen2.5-0.5b
    path('', include('app_llm_classifier.urls')),
    # path('llm/', include('app_llm_classifier.urls')),
    
    # Calling ollama usage
    path('ollama/', include('app_ollama_usage.urls')),
    
    # Sentiment classification with bert
    path('sentiment/', include('app_sentiment_bert.urls')),

    # News classification
    path('news_cls/', include('app_news_classification_bert.urls')),

    path('llm_intro/', include('app_llm_introduction.urls')),

]

# 前面加上一個llm/，這樣就可以在網址中使用/llm/前綴來訪問這些應用
# Force script name for URL prefixing when behind reverse proxy
# FORCE_SCRIPT_NAME = '/llm/' 在settings.py中設定
from django.urls import path
from . import views

app_name = 'app_llm_classifier'

urlpatterns = [
    # Sentiment Analysis
    # 直接進入這個網頁
    path('', views.home_sentiment, name='home_sentiment'),
    path('api_get_sentiment/', views.api_get_sentiment),
    #path('sentiment/', views.home_sentiment, name='home_sentiment'),
    #path('sentiment/api_get_sentiment/', views.api_get_sentiment),
    
    # News Category
    path('news_cate/', views.home_news_category, name='home_news_category'),
    path('news_cate/api_get_news_category/', views.api_get_news_category),
    
    # Qwen Chatbot
    path('chatbot/', views.home_chatbot, name='home_chatbot'),
    path('chatbot/api_get_llm_response/', views.api_get_llm_response),

]

from . import views
from django.urls import path




urlpatterns = [
    path('', views.index, name='index'),
    path('home/login', views.sign_in, name='login'),
    path('home/signup', views.resgitor, name='signup'),
    path('home/reading', views.reading_category_list, name='read_categories'),
    path('reading/<int:category_id>/', views.reading_article_list, name='get_category_readings'),
    path('content/<slug:slug>/', views.reading_detail, name='display_reading_text'),

    path('home/vocbulary_categories', views.get_vocbulary_categories, name='get_vocbulary_categories'),
    path('vocabulary/<int:category_id>/', views.display_vocabulary_list, name='display_vocabulary_list'),

    path('home/listening', views.writing, name='writing'),

    path('listening_category/<int:category_id>/', views.listening_audio_list, name='display_listening_category'),
    path('listening_adio/<slug:slug>/', views.listening_detail, name='display_listening_text'),
    path('home/listening_categories', views.listening_category_list, name='listening_categories'),
    path('ai-chat/', views.ai_chat_handler, name='ai_chat_api'),
    path('home/dashboard', views.dashboard, name='dashboard'),


]

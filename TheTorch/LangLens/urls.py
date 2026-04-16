from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('ogin', views.sign_in, name='login'),
    path('home/signup', views.resgitor, name='signup'),
    path('home/reading', views.reading_category_list, name='read_categories'),
    path('reading/<int:category_id>/', views.reading_article_list, name='get_category_readings'),
    path('content/<slug:slug>/', views.reading_detail, name='display_reading_text'),

    path('home/vocbulary_categories', views.get_vocbulary_categories, name='get_vocbulary_categories'),
    path('vocabulary/<int:category_id>/', views.display_vocabulary_list, name='display_vocabulary_list'),

    path('home/writing', views.writing, name='writing'),

    path('listening_category/<int:category_id>/', views.listening_audio_list, name='display_listening_category'),
    path('listening_adio/<slug:slug>/', views.listening_detail, name='display_listening_text'),
    path('home/listening_categories', views.listening_category_list, name='listening_categories'),
    path('ai-chat/', views.ai_chat_handler, name='ai_chat_api'),
    path('tts/', views.generate_vocabulary_tts, name='generate_vocabulary_tts'),
    path('home/local-news/', views.local_news, name='local_news'),
    path('home/dashboard', views.dashboard, name='dashboard'),
    path('home/profile/edit', views.profile_edit, name='profile_edit'),
    path('home/my-vocabularies', views.my_vocabularies, name='my_vocabularies'),
    path('home/add-vocabulary', views.add_vocabulary, name='add_vocabulary'),
    path('home/edit-vocabulary/<int:vocab_id>/', views.edit_vocabulary, name='edit_vocabulary'),
    path('home/delete-vocabulary/<int:vocab_id>/', views.delete_vocabulary, name='delete_vocabulary'),
    path('home/logout', views.user_logout, name='logout'),
]

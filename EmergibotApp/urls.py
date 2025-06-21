from django.urls import path
from . import views
from EmergibotApp.api import chat_response_api, load_random_questions_from_files



urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('chat-response/', views.chat_response, name='chat_response'),
    path("load-chats/", views.load_chats, name="load_chats"),


    ## APIs
    path("api/v2/chat-response/", chat_response_api, name="chat_response_api"),
    path("api/v2/load-random-questions-from-files/", load_random_questions_from_files, name="load_random_questions_from_files"),
    ## APIs
]


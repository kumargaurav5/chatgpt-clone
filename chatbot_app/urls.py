from django.urls import path
from . import views
import openai



urlpatterns = [
    path('',views.chatbot,name='chatbot'),
    path('login',views.login,name='login'),
    path('register',views.register,name='register'),
    path('logout',views.logout,name='logout'),
    path('accounts/login/', views.login, name='login'),      #added later
    path('accounts/login/register/', views.register, name='register'), #added later
    path('delete_chat_history/', views.delete_chat_history, name ='delete_chat_history')
]
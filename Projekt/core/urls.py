from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autentikace
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Timeline
    path('', views.timeline, name='timeline'),
    
    # Profil
    path('profile/@<str:username>/', views.profile, name='profile'),
    path('profile/edit/', views.profile_update, name='profile_update'),
    path('profile/@<str:username>/following/', views.following_list, name='following_list'),
    path('profile/@<str:username>/followers/', views.followers_list, name='followers_list'),
    
    # Tweety
    path('tweet/<int:pk>/', views.tweet_detail, name='tweet_detail'),
    path('tweet/<int:pk>/delete', views.tweet_delete, name='tweet_delete'),
    
    # Interakce
    path('follow/@<str:username>/', views.follow_toggle, name='follow_toggle'),
    path('like/<int:pk>/<str:content_type>/', views.like_toggle, name='like_toggle'),
    
    # Vyhledávání
    path('search/', views.search, name='search'),
    
    # Hashtagy
    path('hashtag/<str:name>/', views.hashtag_tweets, name='hashtag_tweets'),
    
    # Notifikace
    path('notifications/', views.notifications, name='notifications'),
]
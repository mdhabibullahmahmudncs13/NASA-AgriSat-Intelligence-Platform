from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomAuthToken.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('stats/', views.user_stats, name='user_stats'),
]
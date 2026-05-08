from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

app_name = "users"

urlpatterns = [
    path('register/', views.register, name='register'),
    # aggiungi next_page='menu:index' oppure configura LOGIN_REDIRECT_URL in settings.py
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),

    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('logout2/', views.logout_view, name='logout2'),
    #path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('profile/', views.profile, name='profile'),
]

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'login_register'
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_change/', views.password_change_view, name='password_change'),]
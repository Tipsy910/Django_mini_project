from django.urls import path
from . import views
app_name = 'app'
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('add/', views.add_transaction_view, name='add_transaction'),
    path('categories/add/', views.add_category_view, name='add_category'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/<int:pk>/edit/', views.edit_category_view, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category_view, name='delete_category'),
    path('transaction/<int:pk>/edit/', views.edit_transaction_view, name='edit_transaction'),
    path('transaction/<int:pk>/delete/', views.delete_transaction_view, name='delete_transaction'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),]
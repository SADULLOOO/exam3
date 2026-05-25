from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('edit/', views.update_profile, name='profile_edit'),
]
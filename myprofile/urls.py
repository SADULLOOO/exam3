from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('edit/', views.update_profile, name='profile_edit'),
    path('request-license/', views.request_license_view, name='request_license'),
    path('license-success/', views.license_success_view, name='license_success'),
    path('boss-dashboard/', views.superuser_dashboard_view, name='superuser_dashboard'),
    path('license-toggle/<int:license_id>/', views.toggle_license_status, name='toggle_license'),
]
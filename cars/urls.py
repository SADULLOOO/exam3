from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('brand/<int:brand_id>/', views.brand_detail, name='brand_detail'),
]
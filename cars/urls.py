from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('brand/<int:brand_id>/', views.brand_detail, name='brand_detail'),
    path('model/<int:model_id>/',views.model_detail,name='model_detail'),
    path('car/<int:car_id>/',views.car_detail,name='car_detail'),
    path('search/',views.search,name='search'),
]
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('brand/<int:brand_id>/', views.brand_detail, name='brand_detail'),
    path('model/<int:model_id>/',views.model_detail,name='model_detail'),
    path('car/<int:car_id>/',views.car_detail,name='car_detail'),
    path('search/',views.search,name='search'),
    path('favorite/<int:car_id>/',views.add_favorite,name='add_favorite'),
    path('get_live_time/', views.get_live_time, name='get_live_time'),
    path('heartbeat/', views.heartbeat, name='heartbeat'),
    path('buy/<int:car_id>/',views.buy_car,name='buy_car'),
]
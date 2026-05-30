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
    path('credit/<int:car_id>/',views.take_credit,name='take_credit'),
    path('cancel-order/<int:order_id>/',views.cancel_order,name='cancel_order'),
    path('cancel-credit/<int:credit_id>/',views.cancel_credit,name='cancel_credit'),
    path('about/',views.about,name='about'),
    path('ai/',views.ai_help,name='ai_help'),
    path('chat/<int:car_id>/', views.chat_owner, name='chat_owner'),
    path('chat/admin/list/', views.admin_chat_view, name='chat_admin_list'),
    path('chat/admin/<int:chat_id>/', views.admin_chat_view, name='chat_owner_admin'),
    path('add-car/', views.add_car, name='add_car'),
    path('edit-car/<int:car_id>/', views.edit_car, name='edit_car'),
    path('delete-car/<int:car_id>/', views.delete_car, name='delete_car'),
    path('chat/api/messages/<int:conversation_id>/', views.get_messages_json, name='get_messages_json'),
]

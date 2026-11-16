from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('hotel/<int:pk>/', views.hotel_detail, name='hotel_detail'),
    path('home/', views.home_view, name='home'),
    path('rooms/', views.all_rooms, name='all_rooms'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
]
from django.urls import path
from .views import book_room, booking_success, booked_rooms_list, cancel_booking

app_name = 'bookings'

urlpatterns = [
    path('room/<int:room_id>/book/', book_room, name='book_room'),
    path('success/<int:booking_id>/', booking_success, name='booking_success'),
    path('list/', booked_rooms_list, name='booked_rooms_list'),
    path('cancel/<int:booking_id>/', cancel_booking, name='cancel_booking'),
]
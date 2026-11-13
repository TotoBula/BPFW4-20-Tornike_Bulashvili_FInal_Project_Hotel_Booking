"""
URL configuration for root project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views  # 👈 ეს აუცილებლად გვჭირდება login/logout-ისთვის
from hotels import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # მთავარი გვერდი
    path('', views.home_view, name='home'),
    
    # სასტუმროების გვერდი
    path('hotels/', views.hotel_list, name='hotel_list'),
    
    # კონკრეტული სასტუმროს დეტალური / ნომრების გვერდი
    path('hotels/<int:pk>/', views.hotel_detail, name='hotel_detail'),
    
    # დაჯავშნის ურლი
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),

    # ყველა ნომრის გვერდი
    path('rooms/', views.all_rooms, name='all_rooms'),

    # დაჯავშნილი ნომრების მართვის გვერდი
    path('booked-rooms/', views.booked_rooms_list, name='booked_rooms_list'),
    path('booked-rooms/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # ავტორიზაციის და რეგისტრაციის მისამართები, რომლებიც აკლდა:
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='hotels/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ოთახის დეტალები
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('hotel/<int:pk>/', views.hotel_detail, name='hotel_detail'),
    
    # ავტორიზაციის და რეგისტრაციის მისამართები
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='hotels/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),
    
]
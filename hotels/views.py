from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Hotel, Room
from bookings.models import Booking
from django.core.paginator import Paginator



def hotel_list(request):
    selected_city = request.GET.get('city', '')

    # ყველა უნიკალური ქალაქი ფილტრისთვის
    cities = Hotel.objects.values_list('city', flat=True).distinct()

    # სასტუმროების გაფილტრვა ქალაქის მიხედვით
    if selected_city:
        hotels = Hotel.objects.filter(city=selected_city).order_by('-id')
    else:
        hotels = Hotel.objects.all().order_by('-id')

    # პაგინაცია
    paginator = Paginator(hotels, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'hotels/hotel_list.html',
        {
            'hotels': page_obj,
            'cities': cities,
            'selected_city': selected_city
        },
    )


def hotel_detail(request, pk):
  hotel = get_object_or_404(Hotel, pk=pk)
  rooms = Room.objects.filter(hotel=hotel)

  return render(
      request, 'hotels/hotel_detail.html', {'hotel': hotel, 'rooms': rooms}
  )


def home_view(request):
    # ვფილტრავთ ფავორიტ ნომრებს, ვლაგებთ ახლიდან ძველისკენ მაქსიმუმ 12
    favorite_rooms = Room.objects.filter(is_favorite=True).order_by('-id')[:12]
    
    return render(request, 'hotels/home.html', {'favorite_rooms': favorite_rooms})


def all_rooms(request):
    rooms = Room.objects.all()

    # GET პარამეტრების წამოღება ფორმიდან
    room_type = request.GET.get('room_type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    check_in_str = request.GET.get('check_in', '')
    check_out_str = request.GET.get('check_out', '')
    city = request.GET.get('city', '')  # GET პარამეტრი ქალაქისთვის

    # ფილტრაცია ტიპის მიხედვით
    if room_type:
        rooms = rooms.filter(room_type=room_type)

    # ფილტრაცია ქალაქის მიხედვით (Hotel მოდელის გავლით)
    if city:
        rooms = rooms.filter(hotel__city__icontains=city)

    # ფილტრაცია ფასის დიაპაზონით
    if min_price:
        rooms = rooms.filter(price_per_night__gte=min_price)
    if max_price:
        rooms = rooms.filter(price_per_night__lte=max_price)

    # ფილტრაცია თავისუფალი თარიღების მიხედვით
    if check_in_str and check_out_str:
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()

            if check_in < check_out:
                # ვპოულობთ იმ ოთახების ID-ებს, რომლებიც უკვე დაჯავშნილია ამ პერიოდში
                booked_room_ids = Booking.objects.filter(
                    check_in__lt=check_out, check_out__gt=check_in
                ).values_list('room_id', flat=True)

                # გამოვრიცხავთ დაკავებულ ოთახებს
                rooms = rooms.exclude(id__in=booked_room_ids)
        except ValueError:
            pass

    # --- პაგინაციის ლოგიკა ---
    paginator = Paginator(rooms, 9)  # თითო გვერდზე გამოჩნდება 9 ნომერი
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # უნიკალური ქალაქების სია დროპდაუნისთვის
    cities = Hotel.objects.values_list('city', flat=True).distinct()

    context = {
        'rooms': page_obj,  # ვუშვებთ გვერდების ობიექტს
        'room_types': Room.ROOM_TYPES,
        'cities': cities,
        'selected_type': room_type,
        'min_price': min_price,
        'max_price': max_price,
        'check_in': check_in_str,
        'check_out': check_out_str,
        'selected_city': city,
    }
    return render(request, 'hotels/all_rooms.html', context)

# ოთახის დეტალები
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'hotels/room_detail.html', {'room': room})
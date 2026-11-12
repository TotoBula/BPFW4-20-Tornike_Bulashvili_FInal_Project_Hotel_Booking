from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Booking, Hotel, Room
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


def register(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()  # ვინახავთ ახალ მომხმარებელს ბაზაში
      return redirect('login')  # რეგისტრაციის მერე ვუშვებთ Login გვერდზე
  else:
    form = UserCreationForm()

  return render(request, 'hotels/register.html', {'form': form})


@login_required
def book_room(request, room_id):
  room = get_object_or_404(Room, pk=room_id)
  error_message = None

  existing_bookings = Booking.objects.filter(
      room=room, check_out__gte=datetime.now().date()
  )

  if request.method == 'POST':
    check_in_str = request.POST.get('check_in')
    check_out_str = request.POST.get('check_out')

    # ტექსტური თარიღების გადაყვანა Python-ის date ფორმატში
    check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
    check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()

    # 0. შევამოწმოთ, რომ შესვლის თარიღი არ იყოს წარსულში
    if check_in < datetime.now().date():
      error_message = (
          'წარსული თარიღით დაჯავშნა შეუძლებელია! გთხოვთ აირჩიოთ მომავალი დღე.'
      )

    # 1. შევამოწმოთ, რომ გასვლის თარიღი შესვლაზე გვიანია
    elif check_out <= check_in:
      error_message = 'გასვლის თარიღი უნდა იყოს შესვლის თარიღზე გვიანი!'
    else:
      # 2. შევამოწმოთ, არის თუ არა ეს ოთახი უკვე დაკავებული ამ თარიღებში
      overlapping_bookings = Booking.objects.filter(
          room=room, check_in__lt=check_out, check_out__gt=check_in
      )

      if overlapping_bookings.exists():
        error_message = (
            'ეს ოთახი მითითებულ თარიღებში უკვე დაკავებულია. გთხოვთ აირჩიოთ'
            ' სხვა პერიოდი.'
        )
      else:
        # დღეების რაოდენობის გამოთვლა
        days = (check_out - check_in).days

        if days > 0:
          # ჯამური ფასის გამოთვლა
          total_price = days * room.price_per_night

          # ვქმნით ჯავშანს ბაზისთვის (ფასის ჩათვლით)
          booking = Booking.objects.create(
              user=request.user,
              room=room,
              check_in=check_in,
              check_out=check_out,
              total_price=total_price,
          )
          return redirect('booking_success', booking_id=booking.id)

  return render(
      request,
      'hotels/book_room.html',
      {
          'room': room,
          'error': error_message,
          'existing_bookings': existing_bookings,
      },
  )

@login_required
def booking_success(request, booking_id):
  booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
  return render(request, 'hotels/booking_success.html', {'booking': booking})

def home_view(request):
    # ვფილტრავთ ფავორიტ ნომრებს, ვლაგებთ ახლიდან ძველისკენ და ვზღუდავთ მაქსიმუმ 12-ით
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
    city = request.GET.get('city', '')  # ქალაქის პარამეტრი

    # 1. ფილტრაცია ტიპის მიხედვით
    if room_type:
        rooms = rooms.filter(room_type=room_type)

    # 2. ფილტრაცია ქალაქის მიხედვით (Hotel მოდელის გავლით)
    if city:
        rooms = rooms.filter(hotel__city__icontains=city)

    # 3. ფილტრაცია ფასის დიაპაზონით
    if min_price:
        rooms = rooms.filter(price_per_night__gte=min_price)
    if max_price:
        rooms = rooms.filter(price_per_night__lte=max_price)

    # 4. ფილტრაცია თავისუფალი თარიღების მიხედვით
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
        'rooms': page_obj,  # <--- ვუშვებთ გვერდების ობიექტს
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

def booked_rooms_list(request):
  selected_city = request.GET.get('city', '')

  bookings = Booking.objects.all()

  # ქალაქების მიხედვით გაფილტრვა (სასტუმროს ქალაქის მიხედვით)
  if selected_city:
    bookings = bookings.filter(room__hotel__city=selected_city)

  # ფილტრისთვის ყველა უნიკალური ქალაქის ამოღება
  cities = Hotel.objects.values_list('city', flat=True).distinct()

  context = {
      'bookings': bookings,
      'cities': cities,
      'selected_city': selected_city,
  }
  return render(request, 'hotels/booked_rooms.html', context)


# ჯავშნის გაუქმების (Cancel) ფუნქცია
def cancel_booking(request, booking_id):
  booking = get_object_or_404(Booking, pk=booking_id)
  if request.method == 'POST':
    booking.delete()
    return redirect('booked_rooms_list')
  return render(request, 'hotels/cancel_confirm.html', {'booking': booking})

# ოთახის დეტალები
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'hotels/room_detail.html', {'room': room})
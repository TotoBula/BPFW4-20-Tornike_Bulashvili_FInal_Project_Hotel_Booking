from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Booking
from hotels.models import Hotel, Room  


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

    # შევამოწმოთ, რომ შესვლის თარიღი არ იყოს წარსულში
    if check_in < datetime.now().date():
      error_message = (
          'წარსული თარიღით დაჯავშნა შეუძლებელია! გთხოვთ აირჩიოთ მომავალი დღე.'
      )

    # შევამოწმოთ, რომ გასვლის თარიღი შესვლაზე გვიანია
    elif check_out <= check_in:
      error_message = 'გასვლის თარიღი უნდა იყოს შესვლის თარიღზე გვიანი!'
    else:
      # შევამოწმოთ, არის თუ არა ეს ოთახი უკვე დაკავებული ამ თარიღებში
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
          return redirect('bookings:booking_success', booking_id=booking.id)

  return render(
      request,
      'bookings/book_room.html',
      {
          'room': room,
          'error': error_message,
          'existing_bookings': existing_bookings,
      },
  )

@login_required
def booking_success(request, booking_id):
  booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
  return render(request, 'bookings/booking_success.html', {'booking': booking})


def booked_rooms_list(request):
    selected_city = request.GET.get('city', '')

    # შემოწმება: თუ ადმინია (staff ან superuser), ხედავს ყველას, თუ არა - მხოლოდ საკუთარს
    if request.user.is_staff or request.user.is_superuser:
        bookings = Booking.objects.all()
    else:
        bookings = Booking.objects.filter(user=request.user)

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
    return render(request, 'bookings/booked_rooms.html', context)


# ჯავშნის გაუქმების ფუნქცია
def cancel_booking(request, booking_id):
  booking = get_object_or_404(Booking, pk=booking_id)
  if request.method == 'POST':
    booking.delete()
    return redirect('bookings:booked_rooms_list')
  return render(request, 'bookings/cancel_confirm.html', {'booking': booking})

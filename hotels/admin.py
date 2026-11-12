from django.contrib import admin
from .models import Booking, Hotel, Room

admin.site.register(Hotel)
admin.site.register(Booking)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
  # რა ველები გამოჩნდეს სიის ცხრილში
  list_display = ('title', 'hotel', 'price_per_night', 'is_favorite')
  # რომელი ველების რედაქტირებაა შესაძლებელი პირდაპირ სიიდანვე
  list_editable = ('is_favorite',)
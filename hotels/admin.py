from django.contrib import admin
from .models import Hotel, Room, HotelImage, RoomImage

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 3  # ერთდროულად რამდენი ცარიელი ფოტოს ველი გამოჩნდეს

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 3

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    inlines = [HotelImageInline]
    list_display = ('name', 'city')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    inlines = [RoomImageInline]
    # რა ველები გამოჩნდეს სიის ცხრილში
    list_display = ('title', 'hotel', 'price_per_night', 'is_favorite')
    # რომელი ველების რედაქტირებაა შესაძლებელი პირდაპირ სიიდანვე
    list_editable = ('is_favorite',)
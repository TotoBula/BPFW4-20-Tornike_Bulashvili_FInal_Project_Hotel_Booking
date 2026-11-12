from django.db import models
from django.contrib.auth.models import User

class Hotel(models.Model):
    name = models.CharField(max_length=100, verbose_name="სასტუმროს სახელი")
    city = models.CharField(max_length=50, verbose_name="ქალაქი")
    address = models.CharField(max_length=200, verbose_name="მისამართი")
    image = models.ImageField(upload_to='hotels/', blank=True, null=True, verbose_name="სურათი")

    def __str__(self):
        return f"{self.name} ({self.city})"


class Room(models.Model):
    ROOM_TYPES = (
        ('standard', 'სტანდარტული (Standard)'),
        ('deluxe', 'დელუქსი (Deluxe)'),
        ('suite', 'ლუქსი (Suite)'),
    )

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms', verbose_name="სასტუმრო")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, verbose_name="ნომრის ტიპი")
    title = models.CharField(max_length=100, verbose_name="ნომრის დასახელება")
    price_per_night = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="ფასი (1 ღამე)")
    capacity = models.IntegerField(verbose_name="ტევადობა (ადამიანი)")
    description = models.TextField(verbose_name="აღწერა")
    image = models.ImageField(upload_to='rooms/', blank=True, null=True, verbose_name="ნომრის სურათი")
    is_favorite = models.BooleanField(default=False, verbose_name="ფავორიტი")

    def __str__(self):
        return f"{self.title} - {self.hotel.name}"


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="ნომერი")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="მომხმარებელი")
    check_in = models.DateField(verbose_name="შესვლის თარიღი")
    check_out = models.DateField(verbose_name="გასვლის თარიღი")
    total_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="ჯამური ფასი")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.room.title}"
# Create your models here.

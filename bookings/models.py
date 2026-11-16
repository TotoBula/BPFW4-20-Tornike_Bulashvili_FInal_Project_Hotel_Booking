from django.db import models
from django.contrib.auth.models import User
from hotels.models import Room  

class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="ნომერი")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="მომხმარებელი")
    check_in = models.DateField(verbose_name="შესვლის თარიღი")
    check_out = models.DateField(verbose_name="გასვლის თარიღი")
    total_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="ჯამური ფასი")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.room.title}"

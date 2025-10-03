from django.db import models
from django.contrib.auth.models import User

class Essence(models.Model):
    NOTE_CHOICES = [
        ('TOP', 'Top Note'),
        ('MIDDLE', 'Middle Note'),
        ('BASE', 'Base Note'),
    ]
    name = models.CharField(max_length=100)
    note_type = models.CharField(max_length=10, choices=NOTE_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_note_type_display()})"

class Perfume(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    essences = models.ManyToManyField(Essence, related_name='perfumes')

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Here you can add extra fields for the user profile
    # For example, saved custom blends, order history, etc.

    def __str__(self):
        return self.user.username
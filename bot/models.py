from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=[('manager', 'Manager'), ('employee', 'Employee')])

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Region(models.Model):
    name = models.CharField(max_length=255)  # Optional name/identifier for the region
    points = models.JSONField()  # Store the list of points as JSON

    def __str__(self):
        return self.name or f"Region {self.id}"


class Garbage(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True, null=True)  # Optional description

    def __str__(self):
        return f"Garbage at ({self.latitude}, {self.longitude})"

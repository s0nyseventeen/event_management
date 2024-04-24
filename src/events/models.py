from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    title = models.CharField(
        max_length=200, unique=True, null=False, blank=False
    )
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)


class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

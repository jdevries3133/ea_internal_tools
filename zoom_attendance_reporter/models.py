from django.db import models
from django.contrib.auth.models import User

class UnknownZoomName(models.Model):
    zoom_name = models.CharField(max_length=50, unique=True, blank=False)
    real_name = models.CharField(max_length=50, null=True)

class MeetingCompletedReport(models.Model):
    """
    For updating the frontend of progress. As an alternative to web sockets,
    this will be created after each report is processed, and the frontend
    will just ping the server for progress every few seconds.
    """
    topic = models.CharField(max_length=100)
    meeting_time = models.DateField(auto_now=False, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

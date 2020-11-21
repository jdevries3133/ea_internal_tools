from django.db import models
from django.contrib.auth import get_user_model

from django_mysql.models import JSONField

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
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

class MeetingSetModel(models.Model):
    """
    teacherHelper MeetingSet already has a serialize and deserialize method.
    Once I get the prod database going, we'll store it here.
    """
    owner = models.ForeignKey(get_user_model(), on_delete = models.CASCADE)
    json = JSONField()

from django.db import models
from django.contrib.auth import get_user_model

from django_mysql.models import JSONField

class UnknownZoomName(models.Model):
    zoom_name = models.CharField(max_length=50, unique=True, null=False)
    real_name = models.CharField(max_length=50, null=False)
    meeting_set_model = models.ForeignKey(
        'zar.MeetingSetModel',
        on_delete=models.CASCADE,
        related_name='unknown_names',
    )

class MeetingCompletedReport(models.Model):
    """
    For updating the frontend of progress. As an alternative to web sockets,
    this will be created after each report is processed, and the frontend
    will just ping the server for progress every few seconds.
    """
    topic = models.CharField(max_length=100)
    meeting_time = models.DateField(auto_now=False, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    meeting_set_model = models.ForeignKey(
        'zar.MeetingSetModel',
        on_delete=models.CASCADE,
        related_name='completed_reports',
    )

    def __str__(self):
        return self.topic + ' on ' + self.created.strftime('%m/%d/%y')

class MeetingSetModel(models.Model):
    """
    teacherHelper MeetingSet already has a serialize and deserialize method.
    Once I get the prod database going, we'll store it here.
    """
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    json = JSONField()
    is_processed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

class RawMeetingData(models.Model):
    """
    Straight from the csv file.
    """
    data = models.TextField()
    meeting_set_model = models.ForeignKey(
        'zar.MeetingSetModel',
        on_delete=models.CASCADE,
        related_name='data'
    )

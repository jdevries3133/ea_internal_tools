import logging

from django.db import models
from django.contrib.auth import get_user_model
from django_mysql.models import JSONField

logger = logging.getLogger(__name__)

class UnknownZoomName(models.Model):
    zoom_name = models.CharField(max_length=50, null=False)
    real_name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return f'{self.zoom_name} => {self.real_name}'

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
        return self.topic + ' on ' + self.meeting_time.strftime('%m/%d/%y')

class MeetingSetModel(models.Model):
    """
    teacherHelper MeetingSet already has a serialize and deserialize method.
    Once I get the prod database going, we'll store it here.
    """
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    json = JSONField()
    is_processed = models.BooleanField(default=False)
    needs_name_matching = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

class RawMeetingData(models.Model):
    """
    Straight from the csv file.
    """
    class Meta:
        verbose_name_plural = 'Raw meeting data'

    data = models.TextField()
    meeting_set_model = models.ForeignKey(
        'zar.MeetingSetModel',
        on_delete=models.SET_NULL,
        null=True,
        related_name='data'
    )

    def __str__(self):
        try:
            return (
                self.data.split('\n')[1].split(',')[1]  # topic
                + ' at '
                + self.data.split('\n')[1].split(',')[2]  # datetime
            )
        except Exception as e:
            logger.error(
                'RawMeetingData string method failed to do sloppy csv parsing. '
                f'Exception {e} was thrown'
            )
            return super().__str__()

class Report(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    meeting_set_model = models.ForeignKey(
        'zar.MeetingSetModel',
        on_delete=models.CASCADE,
    )
    report = models.FileField(upload_to='reports/')  # excel workbook
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

from django.db import models

class UnknownZoomName(models.Model):
    zoom_name = models.CharField(max_length=50, unique=True, blank=False)
    real_name = models.CharField(max_length=50, null=True)

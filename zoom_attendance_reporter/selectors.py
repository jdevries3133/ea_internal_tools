from django.contrib.auth.models import User
from django.db.models import Count

from .models import MeetingCompletedReport

def meeting_processing_update(*, user: User) -> dict:
    """
    Returns the last processed meeting to provide an update to the frontend
    after a post request has been made.
    """
    completed_reports = MeetingCompletedReport.objects.filter(
        owner=User).order_by('created').annotate(
            num_completed=Count('id'))
    return {
        'last_completed': completed_reports.last(),
        'num_completed': completed_reports.num_completed
    }

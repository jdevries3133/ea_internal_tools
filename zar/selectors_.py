import logging

from .models import MeetingCompletedReport, MeetingSetModel

logger = logging.getLogger(__name__)

def meeting_processing_update(*, meeting: MeetingSetModel) -> dict:
    """
    Return context for the frontend template where the user is monitoring
    progress.
    """
    num_ahead = MeetingSetModel.objects.filter(
        created__lt=meeting.created,
        is_processed=False
    ).count()
    if not num_ahead:
        processed = MeetingCompletedReport.objects.filter(
            meeting_set_model=meeting
        )
    else:
        processed = []
    if num_ahead > 10:
        logger.critical(
            'There is a queue of more than 10 meetings. This indicates that '
            'the meeting processor may have crashed'
        )
    return {
        'len_queue': num_ahead,
        'processed_meeting_names': [str(m) for m in processed]
    }

def user_has_pending_meeting(*, user):
    """
    Return meeting in progress, or false if there is none.
    """
    try:
        return MeetingSetModel.objects.get(
            owner=user,
            is_processed=False,
        )
    except MeetingSetModel.DoesNotExist:
        return False

def meeting_processing_health_check() -> None:
    """
    Run as a cron to make sure all is well. Checks if any meetingsets at all
    unprocessed; so run it in the middle of the night
    """
    if ct := MeetingSetModel.objects.filter(is_processed=False).count():
        logger.critical(
            f'Overnight meeting processing health check failed. {ct} '
            'MeetingSetModels are unprocessed'
        )

class WipMeetingSetNotFound(Exception):
    pass

def get_wip_meeting_set_model(*, user) -> MeetingSetModel:
    try:
        return MeetingSetModel.objects.get(
            owner=user,
            is_processed=False,
        )
    except (
        MeetingSetModel.DoesNotExist,
        MeetingSetModel.MultipleObjectsReturned
    ):
        raise WipMeetingSetNotFound

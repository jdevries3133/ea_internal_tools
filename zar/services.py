import logging
from typing import List

from teacherHelper.zoom_attendance_report import MeetingSet

from .models import MeetingCompletedReport, MeetingSetModel, RawMeetingData

logger = logging.getLogger(__name__)

def queue_meeting_set(*,
                     data: List[bytes],
                     user,
                     request) -> None:
    """
    Save raw data, and create an empty MeetingSetModel to signal to the
    worker that it has a MeetingSet to process.
    """
    if MeetingSetModel.objects.filter(owner=user, is_processed=False):
        raise Exception(
            f'{user.email} is creating a new MeetingSet despite already having '
            'a MeetingSet in progress.'
        )
    meeting_set_model = MeetingSetModel.objects.create(owner=user)
    RawMeetingData.objects.bulk_create([
        RawMeetingData(
            meeting_set_model=meeting_set_model,
            data=str(f.read(), 'utf-8-sig'),
        ) for f in data
    ])

def process_meeting_set(*,
                        meeting_set_model: MeetingSetModel,
                        data: List[str]) -> None:
    """
    Take an unprocessed MeetingSet and process it! Will be run by a worker
    separate from the web application.
    """
    # initialize MeetingSet
    meeting_set = MeetingSet(data)

    # process all data, create progress reports during processing.
    for meeting in meeting_set.process():
        report = MeetingCompletedReport.objects.create(
            topic=meeting.topic,
            meeting_time=meeting.datetime.date(),
            meeting_set_model=meeting_set_model,
        )
        logger.debug(f'CompletedReport for {report}')

    # update meeting_set_model now that processing is finished.
    meeting_set_model.json = meeting_set.get_serializable_data()
    meeting_set_model.is_processed = True
    meeting_set_model.save()

    # cleanup; delete reports now that processing is done
    MeetingCompletedReport.objects.filter(
        meeting_set_model=meeting_set_model
    ).delete()

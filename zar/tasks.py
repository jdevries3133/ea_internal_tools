import logging
from time import sleep
from pathlib import Path
import os
import sys

import django

sys.path.append(str( BASE_DIR := Path(__file__).resolve().parents[1]))
os.environ['DJANGO_SETTINGS_MODULE'] = 'ea_django_webapps.settings'
django.setup()

# pylint:disable=wrong-import-position
from zar.models import MeetingSetModel, RawMeetingData
from zar.services import process_meeting_set

logger = logging.getLogger(__name__)

def process_meetings():
    """
    Infinitely process MeetingSets.
    """
    while True:

        # select all that need processing
        if msms := MeetingSetModel.objects.filter(is_processed=False).prefetch_related('data'):
            logger.debug(
                f'Begin processing queryset containing {len(msms)} unprocessed meetings.'
            )

            # iterate through them
            for meeting_set_model in msms:
                process_meeting_set(
                    meeting_set_model=meeting_set_model,
                    data=[
                        m.data for m in RawMeetingData.objects.filter(
                            meeting_set_model=meeting_set_model,
                        )
                    ],
                )
        else:
            logger.debug('No meetings to process')

        sleep(3)

if __name__ == '__main__':
    process_meetings()

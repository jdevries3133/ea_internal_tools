"""
Views are listed in order of flow.

1. File Upload
2. Monitor Progress or Cancel
3. Name Match
    skip name match
4. Download Reports

Sometimes, a user gets into a spot in the flow they shouldn't be and
ultimately need to decide where to go next. Hence
no_active_meeting_decision_fork

"""

import logging

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.translation import gettext as _
from teacherHelper.zoom_attendance_report import MeetingSet

from .models import MeetingSetModel, UnknownZoomName
from .services import (
    queue_meeting_set,
    repair_broken_state,
)
from .selectors_ import (
    meeting_processing_update,
    user_has_pending_meeting,
    get_wip_meeting_set_model,
    WipMeetingSetNotFound,
)


logger = logging.getLogger(__name__)

def file_upload(request):
    """
    Upload csv files.
    """
    if user_has_pending_meeting(user=request.user):
        return redirect('monitor_progress')

    class SmallFilesForm(forms.Form):

        file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={
            'multiple': True
        }))

        def __init__(self, *a, **kw):
            # easier to grab raw files before super()
            self.all_files = kw.pop('all_files', [])
            super().__init__(*a, **kw)

        def clean(self):
            super().clean()
            for file in self.all_files:
                if file.size > 1e6:  # 1 mb
                    raise ValidationError(
                        _('CSV should not be larger than 1mb'),
                        code='invalid'
                    )

    if request.method == 'POST':
        form = SmallFilesForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            queue_meeting_set(
                data=request.FILES.getlist('file_field'),
                user=request.user,
            )
            return redirect('monitor_progress')

    form = SmallFilesForm()
    return render(request, 'zar/file_upload.html', {'form': form})

def monitor_progress(request):
    """
    Provide progress reports on very slow MeetingSet.process() method.
    """
    try:
        wip = get_wip_meeting_set_model(user=request.user)
        request.session['wip_ms'] = wip.pk
    except WipMeetingSetNotFound:
        if pk := request.session.get('wip_ms'):
            wip = MeetingSetModel.objects.get(pk=pk)
        else:
            repair_broken_state(user=request.user)
            messages.add_message(
                request,
                messages.ERROR,
                'Something went wrong, please try again.'
            )
            logger.error('Report processing abandoned. Something went wrong')
            return redirect('file_upload')

    if request.method == 'POST':
        logger.info('User cancelled meetingset processing')
        messages.add_message(
            request,
            messages.INFO,
            'Meeting has been cancelled.'
        )
        wip.delete()
        return redirect('file_upload')

    if wip.is_processed:
        # processing is done!
        if wip.needs_name_matching:
            logger.debug(
                'wip meeting_set_model is processed and needs names matched. '
                'Redirecting...'
            )
            return redirect('name_match')

        logger.debug(
            'Name matching has been completed already; user is being '
            'redirected to download their report.'
        )
        return redirect('download_previous_reports')

    return render(
        request,
        'zar/waiting_for_processing.html',
        context={**meeting_processing_update(meeting=wip)}
    )

def name_match(request):
    """
    User matches whacky zoom names with real names if they can.
    """
    class UnknownZoomNamesForm(forms.Form):
        def __init__(self, *a, **kw):
            self.zoom_names = kw.pop('zoom_names')
            super().__init__(*a, **kw)
            for name in self.zoom_names:
                self.fields[name] = forms.CharField(required=False)

        def save(self):
            uzm_objs = []
            for name in self.zoom_names:
                user_data = self.cleaned_data.get(name)
                if user_data:
                    uzm_objs.append(UnknownZoomName(
                        zoom_name=name,
                        real_name=user_data
                    ))
            UnknownZoomName.objects.bulk_create(uzm_objs)

    # fetch the model meeting_set_model in progress that hasn't gone through
    # name matching yet.
    need_matching = MeetingSetModel.objects.filter(
        owner=request.user,
        is_processed=True,
        needs_name_matching=True,
    )

    # redirect to decision fork if there is no current meetingset
    if not need_matching:
        logger.debug(
            'User tried to reach name_match view but has no meetings that need '
            'name matching'
        )
        return redirect('no_active_meeting_decision_fork')

    # Proceed to name matching
    logger.debug(
        f'Proceeding to match missing names for {len(need_matching)} '
        'meeting_set_models'
    )

    if request.method == 'POST':
        form = UnknownZoomNamesForm(
            request.POST,
            zoom_names=request.session.get('unidentifiable')
        )
        if form.is_valid():
            form.save()

            # Update MeetingSetModel state to re-trigger processing with new
            # matches
            MeetingSetModel.objects.filter(
                owner=request.user,
                is_processed=True,
                needs_name_matching=True
            ).update(
                needs_name_matching=False,
                is_processed=False,  # queue for re-processing
            )

            # tell the user why they're not being redirected back to progress
            # monitoring.
            messages.add_message(
                request,
                messages.INFO,
                'Re-processing report data with user provided name-matches.'
            )
            return redirect('monitor_progress')
        else:
            # this form will never not be valid because it's all optional
            # charfields, but nonetheless...
            return render(request, 'zar/name_match.html', {'form': form})

    # compile a list of unknown zoom names from the need_matching queryset
    # fetched earlier.
    all_unidentifiable = set()
    for meeting_set_model in need_matching:  # efficiency could be improved...
        all_unidentifiable.update(
            MeetingSet.deserialize(
                meeting_set_model.json
            ).all_unidentifiable
        )
    all_unidentifiable = list(all_unidentifiable)
    logger.debug(
        'Asking user to match unmatched names: %(unid)s',
                                               {'unid': all_unidentifiable}
    )

    # init form
    request.session['unidentifiable'] = all_unidentifiable
    form = UnknownZoomNamesForm(zoom_names=all_unidentifiable)

    return render(request, 'zar/name_match.html', {'form': form})

def skip_name_match(request):
    """
    Process user's skip name match request and redirect to report download.
    """
    MeetingSetModel.objects.filter(
        owner=request.user,
        is_processed=True,
        needs_name_matching=True
    ).update(needs_name_matching=False)
    return redirect('download_previous_reports')

def download_previous_reports(request):
    """
    Re-download reports previously generated.
    """
    if 'wip_ms' in request.session:
        del request.session['wip_ms']
    return render(request, 'zar/download_previous_report.html')

def no_active_meeting_decision_fork(request):
    """
    If the user tries to access a report processing flow page when they
    have no pending reports, they will be redirected here
    """
    return render(request,'zar/no_active_meeting_decision_fork.html')

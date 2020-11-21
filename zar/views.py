import logging

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .services import make_meeting_set
from .selectors import meeting_processing_update

logger = logging.getLogger(__name__)

def file_upload(request):
    """
    Upload csv files.
    """
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
            meeting_set = make_meeting_set(
                data=request.FILES.getlist('file_field'),
                user=request.user,
                request=request
            )
            return redirect('name_match', meeting_set=meeting_set)

    form = SmallFilesForm()
    return render(request, 'zar/file_upload.html', {'form': form})

def name_match(request):
    """
    User matches whacky zoom names with real names if they can.
    """
    class NameMatch(forms.Form):
        # TODO: make form
        pass

    if request.method == 'POST':
        # TODO: update with matches
        # TODO: generate report
        pass
    unidentifiable = request.session.get('unidentifiable')
    # TODO: render match form
    return render(request, 'zar/name_match.html')

def success(request):
    """
    Allow the user to download their report.
    """
    return JsonResponse({'message': 'success page in progress'})

def ping_process_progress(request):
    """
    Provide progress reports on very slow MeetingSet.process() method.
    """
    return JsonResponse(meeting_processing_update(user=request.user))

def download_sample_report(request):
    """
    Sample report in site header and FAQ
    """
    return HttpResponse('placeholder', content_type='text/plain')

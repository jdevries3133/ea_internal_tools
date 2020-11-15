from django import forms
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .forms import SmallFilesForm
from .services import make_meeting_set
from .selectors import meeting_processing_update

def file_upload(request):
    """
    Upload csv files.
    """
    if request.method == 'POST':
        form = SmallFilesForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            meeting_set = make_meeting_set(
                data=[
                    f for f in request.FILES.getlist('file_field')
                ],
                user=request.user
            )
            return redirect('name_match', meeting_set=meeting_set)

    form = SmallFilesForm()
    return render(request, 'file_upload.html', {'form': form})

def faq(request):
    """
    Provide some additional information.
    """
    pass
    return JsonResponse({'message': 'faq page in progress'})

def name_match(request, meeting_set):
    """
    User matches whacky zoom names with real names if they can.
    """
    pass
    return JsonResponse({'message': 'name_match page in progress'})

def success(request):
    """
    Allow the user to download their report.
    """
    return JsonResponse({'message': 'success page in progress'})

def ping_process_progress(request):
    """
    Provide progress reports on very slow MeetingSet.process() method.
    """
    if request.method != 'GET':
        return JsonResponse({
            'error': True,
            'message': f'Method {request.method} not allowed'
        }, status=403)
    return JsonResponse(meeting_processing_update(user=request.user))

import re

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

class EaMiddlewareException(Exception):
    pass

class EaAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.domain_name = settings.EA_AUTHENTICATION.get('domain_name')
        self.filter_mode = settings.EA_AUTHENTICATION.get('filter_mode')
        self.filter_routes = settings.EA_AUTHENTICATION.get('filter_routes')
        self.request = None
        self.user = None

    def __call__(self, request):
        self.request = request
        self.user = request.user
        if self.need_to_check():
            return self.perform_teacher_check()
        response = self.get_response(request)
        return response

    def perform_teacher_check(self):
        """
        Check if the user is a teacher. If they are not, redirect them to the
        not_validated_yet view.
        """
        if not self.user.is_authenticated:
            messages.add_message(
                self.request,
                messages.INFO,
                'You need to make an account and verify your email before you '
                'can access this page.'
            )
            return redirect('/register/')
        if self.user.role != 'teacher':
            messages.add_message(
                self.request,
                messages.INFO,
                'You need to verify your email before you can access this '
                'page.'
            )
            return redirect('not_verified_yet')
        # check has passed
        return self.get_response(self.request)

    def need_to_check(self) -> bool:
        """
        Based on filter_routes and filter_mode, determine if this route needs
        to be protected.
        """
        for route in self.filter_routes:
            if re.search(route, self.request.path):
                if self.filter_mode == 'whitelist':
                    return False  # don't need to check if we match on whitelist
                if self.filter_mode == 'blacklist':
                    return True  # need to check if we match on blacklist
        # there was no match.
            # no need to check if it's a blacklist
            # do need to check if it's a whitelist.
        return False if self.filter_mode == 'blacklist' else True


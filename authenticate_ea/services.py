from uuid import uuid4

from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

def request_ea_verification(*, user: User) -> None:
    """
    Send the user an email to their EA email address with a link to verify
    that they are EA staff.
    """
    # send_mail(with uuid href)

def ea_email_validator(email: str) -> None:
    """
    Custom form validator raise ValidationError if email does not appear to
    be an @empacad.org email address.
    """
    eml_domain = email.split('@')[1]
    if eml_domain != 'empacad.org':
        print('ind')
        raise ValidationError(_("Email address must be an @empacad.org email"))

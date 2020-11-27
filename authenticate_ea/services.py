from datetime import date, timedelta
import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import EmailConfirmationToken

logger = logging.getLogger(__name__)

User = get_user_model()

def request_email_verification(*, user: User) -> None:
    """
    Send the user an email to their EA email address with a link to verify
    that they are EA staff.
    """
    email_conf_tok = EmailConfirmationToken.objects.create(
        owner=user,
    )
    if not send_mail(
        # subject
        'Email Confirmation Link for Zoom Report Aggregator',
        # message
        'Visit this link to verify your empacad.org email address: '
        f'https://{settings.EA_AUTHENTICATION.get("domain_name")}/'
        f'register/verified/{email_conf_tok.token}/',
        # from
        settings.EMAIL_FROM,
        # to
        [user.email],
        fail_silently=True
    ):
        logger.error(f'Email to {user.email} failed.')

def is_ea(email: str) -> bool:
    """
    Email domain name is "empacad.org"
    """
    eml_domain = email.split('@')[1]
    if eml_domain == 'empacad.org':
        return True
    return False

def is_ea_teacher(email: str):
    """
    Email domain is "empacad.org" and first four characters of email are not
    digits.

        (empacad students' emails start with their student ID)
    """
    if is_ea(email):
        return not email[:4].isnumeric()
    return False

def validate_email_is_ea(email: str) -> None:
    """
    Custom form validator raise ValidationError if email does not appear to
    be an @empacad.org email address.
    """
    # check that the domain is correct at all
    if not is_ea(email):
        raise ValidationError(_("Email address must be an @empacad.org email"))
    if not is_ea_teacher(email):
        raise ValidationError(_("This tool is available for teachers only."))

def assign_user_role_from_slug(*, slug: str) -> User:
    """
    Upon recieving the email validation slug, verify the user and give them a
    role. User will recieve teacher or student role depending on the naming
    pattern of their verified email address.
    """
    token_record = EmailConfirmationToken.objects.get(token=slug)
    user = token_record.owner
    if user.email[:4].isnumeric():
        # students email start with their numerical student id
        user.role = User.STUDENT
        user.save()
    else:
        user.role = User.TEACHER
        user.save()
    return user

def delete_email_tokens(*, user) -> None:
    """
    Delete all validation tokens issued to the user.
    """
    EmailConfirmationToken.objects.filter(owner=user).delete()

def prune_email_tokens() -> None:
    """
    Run as a daily cron job. Delte email tokens that are more than five days
    old.
    """
    EmailConfirmationToken.objects.filter(created__lt=(
        date.today() - timedelta(days=5)
    )).delte()

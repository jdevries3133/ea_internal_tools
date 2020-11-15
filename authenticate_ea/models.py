from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    TEACHER = 0
    STUDENT = 1

    ROLES = (
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student')
    )
    role = models.PositiveSmallIntegerField(choices=ROLES, blank=True, null=True)


class EmailConfirmationToken(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    token = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.token} for {self.owner.username}'


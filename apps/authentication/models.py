from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.authentication.choices import UserTypeChoices
from apps.base.models import BaseModel, SoftDelete


class User(AbstractUser):
    type = models.IntegerField(
        choices=UserTypeChoices.choices, default=UserTypeChoices.PRIVATE
    )
    updated_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(User, self).save(*args, **kwargs)


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(Profile, self).save(*args, **kwargs)
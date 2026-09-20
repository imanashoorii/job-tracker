from django.db import models


class UserTypeChoices(models.IntegerChoices):
    PRIVATE = 1, "HAGHIGHI"
    BUSINESS = 2, "BUSINESS"

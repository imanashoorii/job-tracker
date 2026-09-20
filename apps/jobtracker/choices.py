from django.db import models


class StatusChoices(models.TextChoices):
    APPLIED = "applied", "Applied"
    INTERVIEWING = "interviewing", "Interviewing"
    FINAL_ROUND = "final_round", "Final Round"
    OFFER = "offer", "Offer"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"


class RoundChoices(models.TextChoices):
    NA = "na", "NA"
    FIRST = "1", "1st round"
    SECOND = "2", "2nd round"
    THIRD = "3", "3rd round"
    FOURTH = "4", "4th round"
    FIFTH = "5", "5th round"
    SIXTH = "6", "6th round"
    FINAL = "final", "Final round"
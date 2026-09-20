import re
from general.enum import ValidationPatterns


def validate_phone_number(phone_number: str) -> bool:
    phone_number_pattern = re.match(
        ValidationPatterns.VALIDATE_IRANIAN_PHONE_NUMBER, phone_number
    )
    if phone_number_pattern:
        return True
    return False


def validate_email(email: str) -> bool:
    email_pattern = re.match(ValidationPatterns.VALIDATE_EMAIL, email)
    if email_pattern:
        return True
    return False

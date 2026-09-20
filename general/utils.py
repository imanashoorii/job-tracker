import re
import uuid

from rest_framework.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from general.constants import digits_dict
from general.enum import ValidationPatterns, UserMessages


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def clean_phone_number(phone_number: str) -> tuple[bool, str]:
    is_correct_phone_number = re.match(
        ValidationPatterns.VALIDATE_IRANIAN_PHONE_NUMBER, phone_number
    )
    if not is_correct_phone_number:
        return False, UserMessages.INVALID_PHONE_NUMBER

    sanitized_number = re.sub(r"\D", "", phone_number)

    if sanitized_number.startswith("+98"):
        sanitized_number = "0" + sanitized_number[3:]
    elif sanitized_number.startswith("98"):
        sanitized_number = "0" + sanitized_number[2:]
    elif len(sanitized_number) == 10 and not sanitized_number.startswith("0"):
        sanitized_number = "0" + sanitized_number

    return True, sanitized_number


def normalize_digits(input_text: str):
    input_digits = str(input_text)
    result = ""
    for ltr in input_digits:
        if ltr in digits_dict:
            result += digits_dict[ltr]
        else:
            result += ltr
    return result


def generate_trace_id() -> int:
    trace_id = uuid.uuid4().int & (1 << 32) - 1
    return trace_id


def get_cf_ident(request):
    """
    CLOUDFLARE IDENTIFIER
    Identify the machine making the request by checking HTTP_CF_CONNECTING_IP at first
    if its not provided its original behavior is performed by parsing HTTP_X_FORWARDED_FOR
    if present and number of proxies is > 0. If not use all of
    HTTP_X_FORWARDED_FOR if it is available, if not use REMOTE_ADDR.
    """
    cf_ident = request.META.get("HTTP_CF_CONNECTING_IP", None)

    if cf_ident:
        return cf_ident

    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    remote_addr = request.META.get("REMOTE_ADDR")
    num_proxies = api_settings.NUM_PROXIES

    if num_proxies is not None:
        if num_proxies == 0 or xff is None:
            return remote_addr
        addrs = xff.split(",")
        client_addr = addrs[-min(num_proxies, len(addrs))]
        return client_addr.strip()

    return "".join(xff.split()) if xff else remote_addr


def get_client_ip(request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

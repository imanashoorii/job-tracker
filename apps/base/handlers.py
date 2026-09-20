from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, APIException, PermissionDenied

from general.enum import UserMessages, ErrorCodes, ResultCode


def custom_exception_handler(exc, context):
    """
    Customize the format of error messages in DRF.
    """
    response = exception_handler(exc, context)

    if response is not None and isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "code": ErrorCodes.PERMISSION_DENIED,
                "detail": UserMessages.PERMISSION_DENIED,
            },
            status=status.HTTP_403_FORBIDDEN,
        )
    elif response is not None and isinstance(exc, ValidationError):
        data = response.data
        detail = {}

        if isinstance(data, dict):
            if set(data.keys()) == {"non_field_errors"}:
                value = data["non_field_errors"]
                if isinstance(value, list) and value:
                    detail = value[0]
                else:
                    detail = value
            else:
                for field, messages in data.items():
                    msg = (
                        messages[0]
                        if isinstance(messages, list) and messages
                        else messages
                    )
                    if isinstance(msg, str) and "required" in msg.lower():
                        detail[field] = UserMessages.EMPTY_INPUT_FIELD
                    else:
                        detail[field] = msg

        elif isinstance(data, list) and data:
            detail = data[0]
        else:
            detail = data

        response.data = {
            "success": False,
            "code": ResultCode.FAILED,
            "detail": detail,
        }
    elif response is not None and isinstance(exc, APIException):
        exception_message = {
            "success": False,
            "code": getattr(exc, "default_code", "error"),
            "detail": getattr(exc, "default_detail", ""),
        }
        response.data = exception_message

    return response

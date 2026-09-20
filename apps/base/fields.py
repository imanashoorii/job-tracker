import base64
import mimetypes

from django.core.files.storage import default_storage

from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField, Base64FieldMixin, Base64FileField

from general.enum import UserMessages
from general.jalali import jalali_datetime, pretty_jalali_datetime


class JalaliDateTimeField(serializers.Field):
    """
    Sample returned data: 1403/08/27-16:04:55
    """

    def to_representation(self, value):
        return jalali_datetime(value, time=True)

    def to_internal_value(self, data):
        return


class JalaliDateField(serializers.Field):
    """
    Sample returned data: 1403/08/27
    """

    def to_representation(self, value):
        return jalali_datetime(value, time=False)

    def to_internal_value(self, data):
        return


class PrettyJalaliDateTimeField(serializers.Field):
    """
    Sample returned data: یکشنبه ۲۷ آبان ۱۴۰۳ 16:04:55
    """

    def to_representation(self, value):
        return pretty_jalali_datetime(value)

    def to_internal_value(self, data):
        return


class CustomBase64ImageField(Base64ImageField):
    ALLOWED_TYPES = (
        "jpeg",
        "jpg",
        "png",
    )
    INVALID_FILE_MESSAGE = UserMessages.INVALID_FILE_MESSAGE
    INVALID_TYPE_MESSAGE = UserMessages.INVALID_TYPE_MESSAGE

    def to_representation(self, file):
        """
        Custom to_representation method to handle base64 encoding.
        This method ensures the image file is valid before base64 encoding.
        """
        if self.represent_in_base64:
            if not file:
                return ""
            try:
                with default_storage.open(file.name, "rb") as f:
                    file_content = f.read()
                    base64_image = base64.b64encode(file_content).decode()
                    mime_type = self.get_file_extension(file.name, file_content)
                    return f"data:image/{mime_type};base64,{base64_image}"

            except Exception:
                raise IOError("Error encoding file")
        else:
            return super(Base64FieldMixin, self).to_representation(file)


class CustomBase64FileField(Base64FileField):
    ALLOWED_TYPES = (
        "jpeg",
        "jpg",
        "png",
        "svg",
        "pdf",
    )
    INVALID_FILE_MESSAGE = UserMessages.INVALID_FILE_MESSAGE
    INVALID_TYPE_MESSAGE = UserMessages.INVALID_TYPE_MESSAGE

    def get_file_extension(self, filename, decoded_file):
        """
        Return the file extension based on the guessed MIME type from the file name.
        """
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            return None
        return mime_type.split("/")[-1]

    def to_representation(self, file):
        """
        Encode file as base64 with proper MIME type prefix.
        """
        if self.represent_in_base64:
            if not file:
                return ""
            try:
                with default_storage.open(file.name, "rb") as f:
                    file_content = f.read()
                    extension = self.get_file_extension(file.name, file_content)

                    if not extension or extension.lower() not in self.ALLOWED_TYPES:
                        raise ValueError(self.INVALID_TYPE_MESSAGE)

                    mime_type, _ = mimetypes.guess_type(file.name)
                    base64_file = base64.b64encode(file_content).decode()
                    return f"data:{mime_type};base64,{base64_file}"
            except Exception:
                raise IOError(self.INVALID_FILE_MESSAGE)
        else:
            return super().to_representation(file)

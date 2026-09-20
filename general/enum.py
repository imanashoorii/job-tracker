class ErrorCodes:
    MALFORMED_DATA = "malformed_data"
    INVALID_CREDENTIALS = "wrong_credentials"
    INVALID_TOTP_CODE = "invalid_totp"
    INVALID_PHONE_NUMBER = "invalid_phone_number"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    NEGATIVE_AMOUNT = "negative_amount"
    OTP_NOT_SEND = "otp_not_send"
    PERMISSION_DENIED = "permission_denied"
    OBJ_NOT_EDITABLE = "not_editable"


class UserMessages:
    MALFORMED_DATA = "اطلاعات وارد شده معتبر نیست"
    INVALID_CREDENTIALS = "نام کاربری یا رمزعبور وارد شده اشتباه است"
    INVALID_TOTP_CODE = "رمز یک بار مصرف نامعتبر است"
    INVALID_PHONE_NUMBER = "شماره تلفن وارد شده نامعتبر است"
    EMPTY_INPUT_FIELD = "این فیلد الزامی است"
    OTP_SEND = "رمز یکبار مصرف ارسال شد"
    SMS_NOT_SEND = "خطا در ارسال پیامک"
    LOGIN_OTP_ERROR = (
        "شماره موبایل یا رمز وارد شده صحیح نمی‌باشد یا کد شما منقضی شده است"
    )
    SUCCESS = "موفق"
    INSUFFICIENT_BALANCE = "مبلغ درخواستی از موجودی شما بیشتر می‌باشد"
    NEGATIVE_AMOUNT = "مبلغ نمیتواند کمتر از صفر باشد"
    PERMISSION_DENIED = "شما اجازه دسترسی به این قسمت را ندارید"
    INVALID_FILE_MESSAGE = "فایل معتبر نمیباشد"
    INVALID_TYPE_MESSAGE = "فرمت فایل صحیح نمیباشد"
    OBJ_NOT_EDITABLE = "امکان ویرایش وجود ندارد"
    TICKET_IS_CLOSED = "تیکت بسسته شده است"
    INVALID_API_KEY = "پارامتر apiKey نامعتبر است"
    INACTIVE_API_KEY = "توکن apiKey شما غیرفعال است"
    INVALID_IP = "آدرس IP نامعتبر است"
    NOT_FOUND = "موردی یافت نشد"
    NOT_ALLOWED = "انجام این عملیات مجاز نیست"
    USERNAME_TAKEN = "username has already been taken"
    EMAIL_TAKEN = "email has already been used"
    PASSWORDS_DO_NOT_MATCH = "passwords do not match"


class ResultCode:
    SUCCESS = 1
    FAILED = -1
    NOT_FOUND = -2
    NOT_ALLOWED = -3

    INVALID_API_KEY = -1001
    INACTIVE_API_KEY = -1002
    INVALID_IP = -1003


class SMSTemplates:
    SEND_LOGIN_OTP = "otp-login"


class ValidationPatterns:
    VALIDATE_EMAIL = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    VALIDATE_IRANIAN_PHONE_NUMBER = r"^(\+98|98|0)?9[0-9]{9}$"


class CacheKeys:
    OTP_KEY = "otp_{phone_number}"
    GAUTH_KEY = "gauth_{username}"

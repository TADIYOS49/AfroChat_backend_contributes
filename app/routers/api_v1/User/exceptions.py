from app.exceptions import (
    AuthFailedHTTPException,
    AuthTokenExpiredHTTPException,
    BadRequestHTTPException,
    NotFoundHTTPException,
    ServiceNotAvailableHTTPException,
)

USER_NAME_IS_TAKEN = BadRequestHTTPException(msg="Username is already taken")
USER_NOT_ACTIVATED: BadRequestHTTPException = BadRequestHTTPException(
    msg="User is not activated"
)

USER_NOT_FOUND = NotFoundHTTPException("User Not Found")

USER_ALREADY_ACTIVATED = BadRequestHTTPException(msg="user is already activated")

USER_NOT_ACTIVATED = BadRequestHTTPException(msg="user is not activated")

USER_DOESNT_HAVE_PASSWORD = BadRequestHTTPException(msg="user doesn't have a password")

PHONE_NUMBER_OR_EMAIL_MUST_BE_PROVIDED = BadRequestHTTPException(
    msg="Phone number or email must be provided for signup"
)

EMAIL_HAS_BEEN_REGISTERED = BadRequestHTTPException(
    msg="email address has already been registered!"
)

PHONE_HAS_BEEN_REGISTERED = BadRequestHTTPException(
    msg="phone number has already been registered"
)

UN_AUTHORIZED_ACCESS = AuthFailedHTTPException("Not Authenticated")

PERMISSION_NOT_ALLOWED = AuthFailedHTTPException(
    "You don't have permission to create users with the specified role"
)

UN_AUTHORIZED_ACCESS_ADMIN = AuthFailedHTTPException("Not admin")

GOOGLE_AUTH_FAILED = BadRequestHTTPException(msg="Google Auth Failed")

INVALID_CREDENTIAL = BadRequestHTTPException("Could not validate Credentials")
INCORRECT_PASSWORD = BadRequestHTTPException(msg="Incorrect password")

TOKEN_EXPIRED = AuthTokenExpiredHTTPException()

OTP_EXPIRED = BadRequestHTTPException(msg="OTP has expired")

OTP_NOT_FOUND = NotFoundHTTPException(msg="OTP not found")

OTP_VALIDATION_FAILED = BadRequestHTTPException(msg="OTP validation failed")

# error sending sms message

ERROR_SENDING_SMS_MESSAGE = ServiceNotAvailableHTTPException(
    msg="We're currently experiencing issues with our SMS service. Please try again later."
)

# Telegram Validation failed

TelegramValidationFailed = BadRequestHTTPException(
    msg="Telegram Validation failed. Please send the correct data"
)

# invalid Telegram Credentials

InvalidTelegramCredentials = BadRequestHTTPException(msg="Invalid Telegram Credentials")

# case -> telegram_id have to be sent inside request

TelegramIdNotSent = BadRequestHTTPException(
    msg="Telegram Id have to be sent inside request"
)

# Already have telegram account

AlreadyHaveTelegramAccount = BadRequestHTTPException(
    msg="You already have telegram account"
)

# Invalid Credentials

SMTPAuthenticationError = BadRequestHTTPException(
    msg="SMTP Authentication Error: Check your email credentials."
)

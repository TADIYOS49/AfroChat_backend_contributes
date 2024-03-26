from app.exceptions import (
    AuthFailedHTTPException,
    AuthTokenExpiredHTTPException,
    BadRequestHTTPException,
    NotFoundHTTPException,
    ServiceNotAvailableHTTPException,
    TooManyRequestsException,
)

USER_NAME_IS_TAKEN = BadRequestHTTPException(msg="Username is already taken")
USER_NOT_ACTIVATED: BadRequestHTTPException = BadRequestHTTPException(
    msg="User is not activated"
)

USER_NOT_FOUND = NotFoundHTTPException("User Not Found")

USER_ALREADY_ACTIVATED = BadRequestHTTPException(msg="user is already activated")

TOO_MANY_CHAT_REQUESTS = TooManyRequestsException(
    msg="You made too many chat requests in one day please wait for 24 hours before making any more requests"
)

TOO_MANY_IMAGE_REQUESTS = TooManyRequestsException(
    msg="You made too many image requests in one day please wait for 24 hours before making any more requests"
)

TOO_MANY_PERSONAS_CREATED = TooManyRequestsException(
    msg="You created too many personas in one day please wait for 24 hours before making any more requests"
)

USER_NOT_ACTIVATED = BadRequestHTTPException(msg="user is not activated")

USER_DOESNT_HAVE_PASSWORD = BadRequestHTTPException(msg="user doesn't have a password")

PHONE_NUMBER_OR_EMAIL_MUST_BE_PROVIDED = BadRequestHTTPException(
    msg="Phone number or email must be provided for signup"
)

EMAIL_MUST_BE_PROVIDED = BadRequestHTTPException(
    msg="Email must be provided for signup"
)

EMAIL_HAS_BEEN_REGISTERED = BadRequestHTTPException(
    msg="email address has already been registered!"
)

PHONE_HAS_BEEN_REGISTERED = BadRequestHTTPException(
    msg="phone number has already been registered"
)

UN_AUTHORIZED_ACCESS = AuthFailedHTTPException("Not Authenticated")

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

TelegramIDAlreadyInUse = BadRequestHTTPException(msg="Telegram Id already in use")

BotsNotAllowed = BadRequestHTTPException(msg="Bots are not allowed to register")

RECAPTCHA_FAILED = BadRequestHTTPException(msg="Recaptcha failed")

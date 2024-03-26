from app.exceptions import NotFoundHTTPException, ServiceNotAvailableHTTPException


SUBSCRIPTION_PLAN_NOT_FOUND = NotFoundHTTPException("subscription plan not found!")
PAYMENT_NOT_FOUND = NotFoundHTTPException("payment not found!")
SERIVCE_NOT_AVAILABLE = ServiceNotAvailableHTTPException("service not available!")

from constants.status_codes import StatusCodes


class BaseCustomHTTPException(Exception):
    """
    This is a base class for all custom HTTP exceptions. It is used to create custom HTTP exceptions with a custom message and status code.

    :param message: The message to be sent in the response body.
    :param status_code: The status code to be sent in the response body.
    :param isCustom: A boolean value to indicate whether the exception is a custom exception raised by the BaseCustomHTTPException class or not.
    """

    def __init__(self, message, status_code):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.isCustom = True

    @staticmethod
    def bad_request(message):
        return BaseCustomHTTPException(message, StatusCodes.BAD_REQUEST.value)

    @staticmethod
    def unauthorized(message):
        return BaseCustomHTTPException(message, StatusCodes.UNAUTHORIZED.value)

    @staticmethod
    def not_found(message):
        return BaseCustomHTTPException(message, StatusCodes.NOT_FOUND.value)

    @staticmethod
    def conflict(message):
        return BaseCustomHTTPException(message, StatusCodes.CONFLICT.value)

    @staticmethod
    def forbidden(message):
        return BaseCustomHTTPException(message, StatusCodes.FORBIDDEN.value)

    @staticmethod
    def internal_server_error(message):
        return BaseCustomHTTPException(message, StatusCodes.INTERNAL_SERVER_ERROR.value)

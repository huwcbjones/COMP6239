from tornado.web import HTTPError


class ProcessingException(HTTPError):

    def __init__(self, status_code, message=None, log_message=None):
        # self.traceback = [l.strip() for l in traceback.format_stack()][:-2]
        if log_message is None:
            log_message = message
        self.message = message
        super().__init__(status_code, log_message=log_message)


class NotFoundException(ProcessingException):

    def __init__(self, message=None, log_message=None):
        super().__init__(404, message, log_message)


class BadRequestException(ProcessingException):

    def __init__(self, message=None, log_message=None):
        super().__init__(400, message, log_message)


class UnauthorisedException(ProcessingException):

    def __init__(self, message=None, log_message=None):
        super().__init__(401, message, log_message)


class AccessDeniedException(ProcessingException):

    def __init__(self, message=None, log_message=None):
        super().__init__(403, message, log_message)


class ResourceAlreadyExistsException(ProcessingException):

    def __init__(self, message=None, log_message=None):
        super().__init__(409, message, log_message)


class RateLimitExceededException(ProcessingException):

    def __init__(self, log_message=None):
        super().__init__(429, message="Rate limit exceeded", log_message=log_message)


class ServerErrorException(ProcessingException):

    def __init__(self, message: str = "Internal Server Error", exception: Exception=None):
        # if exception is not None:
        #     super().__init__(500, reason)
        # else:
        #     super().__init__(500, reason)
        super().__init__(500, message=message, log_message=str(exception))

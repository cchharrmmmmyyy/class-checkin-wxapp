class ServiceException(Exception):

    def __init__(self, message, code=1, http_status=400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.http_status = http_status


class AuthenticationException(Exception):

    def __init__(self, message, code=401, http_status=401):
        super().__init__(message)
        self.message = message
        self.code = code
        self.http_status = http_status

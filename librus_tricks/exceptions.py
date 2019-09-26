class LibrusTricksException(Exception):
    pass


class LibrusTricksAuthException(LibrusTricksException):
    pass


class LibrusTricksAPIException(LibrusTricksAuthException):
    pass


class LibrusLoginError(LibrusTricksAuthException):
    pass


class SynergiaAPIEndpointNotFound(LibrusTricksAPIException):
    pass


class LibrusPortalInvalidPasswordError(LibrusTricksAuthException):
    pass


class SynergiaAccessDenied(LibrusTricksAPIException):
    pass


class WrongHTTPMethod(Exception):
    pass


class SynergiaAPIInvalidRequest(LibrusTricksAPIException):
    pass


class TokenExpired(LibrusTricksException):
    pass


class SynergiaForbidden(LibrusTricksAPIException):
    pass


class InvalidCacheManager(LibrusTricksAuthException):
    pass


class CaptchaRequired(LibrusTricksAuthException):
    pass


class SynergiaServerError(LibrusTricksAPIException):
    pass

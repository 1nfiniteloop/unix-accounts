

class UnixAccountError(Exception):
    pass


class NotPossible(UnixAccountError):
    pass


class DoesNotExist(UnixAccountError):
    pass


class AlreadyExist(UnixAccountError):
    pass


class InternalError(UnixAccountError):
    pass

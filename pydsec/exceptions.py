class Error(Exception):
    pass


class Unavailable(Error):
    pass


class InternalServerError(Error):
    pass

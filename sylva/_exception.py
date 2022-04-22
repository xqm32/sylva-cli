__all__ = ["LoginError", "UnknownCommand", "UnexpectedCode"]


class LoginError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class UnknownCommand(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class UnexpectedCode(Exception):
    def __init__(self, *args):
        super().__init__(*args)

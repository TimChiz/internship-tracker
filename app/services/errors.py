"""Custom errors raised by the services layer."""


class AuthError(Exception):
    """Raised when sign-up or login can't go ahead, e.g. the email is taken.

    The message is safe to show to the user.
    """

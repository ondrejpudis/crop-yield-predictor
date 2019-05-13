from functools import wraps
from time import sleep

from ee.ee_exception import EEException

from .logger.console_logger import LOGGER


def retry_api_call(n_times: int, sleep_time: float = 5.0):
    """Repeat the call n times."""

    def inner(func):
        @wraps(func)
        def closure(*args, **kwargs):
            repeats = n_times
            while repeats:
                try:
                    return func(*args, **kwargs)
                except EEException as exc:
                    repeats -= 1
                    if repeats == 0:
                        raise exc
                    LOGGER.error(f"ERROR, server computation, {exc.__str__()}")
                    sleep(sleep_time)

        return closure

    return inner

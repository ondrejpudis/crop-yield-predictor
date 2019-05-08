from functools import wraps
from logging import Formatter, getLevelName, getLogger, StreamHandler

logger = getLogger()
logger.setLevel(getLevelName("INFO"))

log_formatter = Formatter("%(asctime)s %(message)s [%(threadName)s] ")
console_handler = StreamHandler()
console_handler.setFormatter(log_formatter)

logger.addHandler(console_handler)


def console_log(func):
    @wraps(func)
    def inner(*args, **kwargs):
        logger.info(f"START {func.__name__} {args[0].district_name}")
        result = func(*args, **kwargs)
        logger.info(f"STOP {func.__name__} {args[0].district_name}")
        return result

    return inner

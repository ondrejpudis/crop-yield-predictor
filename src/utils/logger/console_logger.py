from logging import Formatter, getLevelName, getLogger, StreamHandler


def _get_logger():
    """Set the logger behaviour."""
    logger = getLogger()
    logger.setLevel(getLevelName("INFO"))

    log_formatter = Formatter("%(asctime)s %(message)s [%(threadName)s] ")
    console_handler = StreamHandler()
    console_handler.setFormatter(log_formatter)

    logger.addHandler(console_handler)
    return logger


LOGGER = _get_logger()

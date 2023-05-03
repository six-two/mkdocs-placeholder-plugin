# This module contains all the CMS / site generator independent code

class PlaceholderConfigError(Exception):
    """
    A custom exception class, that denotes critical errors in the configuration (file)
    """
    pass


class PlaceholderPageError(Exception):
    """
    A custom exception class, that denotes critical errors in the currently processed page
    """
    pass


import logging

# Set up a logger for my code to use
LOGGER = logging.getLogger("dev.six-two.placeholder-plugin")

_WARNINGS_ENABLED = True

def set_logger(logger: logging.Logger) -> None:
    global LOGGER
    LOGGER = logger


def set_warnings_enabled(value: bool) -> None:
    global _WARNINGS_ENABLED
    _WARNINGS_ENABLED = value


def warning(message: str) -> None:
    if _WARNINGS_ENABLED:
        LOGGER.warning(f"[placeholder] {message}")

def debug(message: str) -> None:
    LOGGER.debug(f"[placeholder] {message}")


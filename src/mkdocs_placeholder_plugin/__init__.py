import logging
from mkdocs.utils import warning_filter

# Set up a logger for my code to use
LOGGER = logging.getLogger("mkdocs.plugins.placeholder")
LOGGER.addFilter(warning_filter)

_WARNINGS_ENABLED = True


def set_warnings_enabled(value: bool) -> None:
    global _WARNINGS_ENABLED
    _WARNINGS_ENABLED = value


def warning(message: str) -> None:
    if _WARNINGS_ENABLED:
        LOGGER.warning(f"[placeholder] {message}")

def debug(message: str) -> None:
    LOGGER.debug(f"[placeholder] {message}")


# Import local files in the correct order
from .plugin import PlaceholderPlugin

__all__ = ["PlaceholderPlugin",]

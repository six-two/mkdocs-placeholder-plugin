import logging
from mkdocs.utils import warning_filter

# Set up a logger for my code to use
LOGGER = logging.getLogger(f"mkdocs.plugins.placeholder")
LOGGER.addFilter(warning_filter)

def warning(message: str) -> None:
    LOGGER.warning(f"[placeholder] {message}")

# Import local files in the correct order
from .plugin import PlaceholderPlugin

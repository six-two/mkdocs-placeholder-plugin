from ..generic import LOGGER
from mkdocs.utils import warning_filter

LOGGER.addFilter(warning_filter)

# Import local files in the correct order
from .plugin import PlaceholderPlugin

__all__ = ["PlaceholderPlugin",]

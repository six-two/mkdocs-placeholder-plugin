import html
import random
import string
import time
# local
from .config import PlaceholderConfig

SAFE_CHARS_IN_MARKDOWN = list(string.ascii_letters + string.digits)

def paraniod_html_escape(input: str) -> str:
    """
    Escapes every character as HTML entities except a couple allow listed ones.
    Why? Because a lot of characters can cause unwanted problems in markdown parsing (*, \n, _, `, (, |, space, etc).
    """
    return "".join([char if char in SAFE_CHARS_IN_MARKDOWN else f"&#{ord(char)};"
         for char in input])

class DynamicPlaceholderPreprocessor:
    """
    This class replaces dynamic placeholders with the same elements as the javascript would.
    However, if JavaScript is disabled, it will show the default value instead of the placeholder name.
    """
    def __init__(self, config: PlaceholderConfig) -> None:
        self.config = config
        self.unique = f"{int(time.time())}_{random.randint(0, 10000)}"

    def handle_markdown_page(self, page_markdown: str) -> str:
        # This works similar to safe_replace_multiple_placeholders_in_string in replacer.ts.
        # The roundabout way is needed to ensure that placeholders that are in a previously replaced placeholder's value are not replaced
        for placeholder in self.config.placeholders.values():
            replace_with_value = f"x{placeholder.name}_{self.unique}x"

            # Handle explicitely maked dynamic placeholders
            search_expression = self.config.settings.dynamic_prefix + placeholder.name + self.config.settings.dynamic_suffix
            page_markdown = page_markdown.replace(search_expression, replace_with_value)

            # Handle normal placeholders, whic are currently just an alias for dynamic placeholders
            search_expression = self.config.settings.normal_prefix + placeholder.name + self.config.settings.normal_suffix
            page_markdown = page_markdown.replace(search_expression, replace_with_value)
        
        return page_markdown

    def handle_html_page(self, page_html: str) -> str:
        # needs to happen in the HTML document, since otherwise listings will screw things up
        for placeholder in self.config.placeholders.values():
            search_expression = f"x{placeholder.name}_{self.unique}x"
            placeholder_default_value = "Please enable JavaScript" if placeholder.default_function else placeholder.default_value
            # no need to escape the placeholder name, since I do strict validation on it when I parse the placeholders
            replace_with_value = f'<span class="placeholder-value" data-placeholder="{placeholder.name}">{html.escape(placeholder_default_value)}</span>'
            page_html = page_html.replace(search_expression, replace_with_value)

        return page_html


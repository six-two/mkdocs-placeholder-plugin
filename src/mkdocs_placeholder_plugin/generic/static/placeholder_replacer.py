import html
import random
import string
import time
# local
from ..config import PlaceholderConfig, Placeholder, InputType

SAFE_CHARS_IN_MARKDOWN = list(string.ascii_letters + string.digits)

def paraniod_html_escape(input: str) -> str:
    """
    Escapes every character as HTML entities except a couple allow listed ones.
    Why? Because a lot of characters can cause unwanted problems in markdown parsing (*, \n, _, `, (, |, space, etc).
    """
    return "".join([char if char in SAFE_CHARS_IN_MARKDOWN else f"&#{ord(char)};"
         for char in input])

def html_for_dynamic_placeholder(placeholder: Placeholder) -> str:
    placeholder_default_value = "Please enable JavaScript" if placeholder.default_function else get_default_placeholder_value(placeholder)
    # no need to escape the placeholder name, since I do strict validation on it when I parse the placeholders
    return f'<span class="placeholder-value" data-placeholder="{placeholder.name}">{html.escape(placeholder_default_value)}</span>'


def get_default_placeholder_value(placeholder: Placeholder) -> str:
    if placeholder.input_type == InputType.Checkbox:
        default_value = placeholder.default_value or "unchecked"
        return placeholder.values[default_value]
    elif placeholder.input_type == InputType.Dropdown:
        if placeholder.default_value:
            return placeholder.values[placeholder.default_value]
        else:
            return list(placeholder.values.values())[0]
    elif placeholder.input_type == InputType.Field:
        return placeholder.default_value
    else:
        raise Exception(f"Unknown input type: {placeholder.input_type}")


class DynamicPlaceholderPreprocessor:
    """
    This class replaces dynamic placeholders with the same elements as the javascript would.
    However, if JavaScript is disabled, it will show the default value instead of the placeholder name.
    """
    def __init__(self, config: PlaceholderConfig) -> None:
        self.config = config
        self.unique = f"{int(time.time())}_{random.randint(0, 10000)}"

    def handle_markdown_page(self, page_markdown: str) -> str:
        # Mark placeholders to replace in the Markdown, so that the automatic input tables, input replacements, etc

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
            replace_with_value = html_for_dynamic_placeholder(placeholder)
            page_html = page_html.replace(search_expression, replace_with_value)

        return page_html


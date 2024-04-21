import html
import random
import string
import time
# local
from ..config import PlaceholderConfig, Placeholder

SAFE_CHARS_IN_MARKDOWN = list(string.ascii_letters + string.digits)
CACHED_EXPANDED_DEFAULT_VALUES: dict[str,str] = {}

def paraniod_html_escape(input: str) -> str:
    """
    Escapes every character as HTML entities except a couple allow listed ones.
    Why? Because a lot of characters can cause unwanted problems in markdown parsing (*, \n, _, `, (, |, space, etc).
    """
    return "".join([char if char in SAFE_CHARS_IN_MARKDOWN else f"&#{ord(char)};"
         for char in input])

def html_for_dynamic_placeholder(placeholder: Placeholder, config: PlaceholderConfig) -> str:
    placeholder_default_value = placeholder_expanded_default_value(placeholder, config)
    # no need to escape the placeholder name, since I do strict validation on it when I parse the placeholders
    return f'<span class="placeholder-value placeholder-value-static" data-placeholder="{placeholder.name}">{html.escape(placeholder_default_value)}</span>'

def html_for_editable_placeholder(placeholder: Placeholder, config: PlaceholderConfig) -> str:
    placeholder_default_value = placeholder_expanded_default_value(placeholder, config)
    # no need to escape the placeholder name, since I do strict validation on it when I parse the placeholders
    return f'<span class="placeholder-value inline-editor-requested" data-placeholder="{placeholder.name}">{html.escape(placeholder_default_value)}</span>'


def get_all_placeholder_patterns(placeholder: Placeholder, config: PlaceholderConfig) -> list[str]:
    s = config.settings
    return [
        s.editable_prefix + placeholder.name + s.editable_suffix,
        s.dynamic_prefix + placeholder.name + s.dynamic_suffix,
        s.html_prefix + placeholder.name + s.html_suffix,
        s.normal_prefix + placeholder.name + s.normal_suffix,
        s.static_prefix + placeholder.name + s.static_suffix,
    ]

def placeholder_expanded_default_value(placeholder: Placeholder, config: PlaceholderConfig) -> str:
    # This speeds up the somewhat expensive operation by caching the results
    value = CACHED_EXPANDED_DEFAULT_VALUES.get(placeholder.name)
    if value is None:
        value = _placeholder_expanded_default_value(placeholder, config)
        CACHED_EXPANDED_DEFAULT_VALUES[placeholder.name] = value
    return value

def _placeholder_expanded_default_value(placeholder: Placeholder, config: PlaceholderConfig) -> str:
    if placeholder.default_function:
        return "<JAVASCRIPT_FUNCTION>"

    default_value = placeholder.default_value
    if placeholder.values:
        default_value = placeholder.values[default_value]

    if not placeholder.allow_nested:
        return default_value
    else:
        # This works similar to safe_replace_multiple_placeholders_in_string in replacer.ts.
        # The roundabout way is needed to ensure that placeholders that are in a previously replaced placeholder's value are not replaced
        string = default_value
        unique = f"{int(time.time())}_{random.randint(0, 10000)}"
        for placeholder in config.placeholders.values():
            for pattern in get_all_placeholder_patterns(placeholder, config):
                string = string.replace(pattern, f"x{placeholder.name}_{unique}x")

        for placeholder in config.placeholders.values():
            pattern = f"x{placeholder.name}_{unique}x"
            if pattern in string:
                expanded_value = placeholder_expanded_default_value(placeholder, config)
                string = string.replace(pattern, expanded_value)

        return string


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
            # Handle explicitly marked dynamic placeholders
            search_expression = self.config.settings.dynamic_prefix + placeholder.name + self.config.settings.dynamic_suffix
            page_markdown = page_markdown.replace(search_expression, f"x{placeholder.name}_{self.unique}_DYNAMICx")

            # Handle explicitly marked editable placeholders
            search_expression = self.config.settings.editable_prefix + placeholder.name + self.config.settings.editable_suffix
            page_markdown = page_markdown.replace(search_expression, f"x{placeholder.name}_{self.unique}_EDITABLEx")

            # Handle normal placeholders, if they are just an alias for dynamic or editable placeholders
            if self.config.settings.normal_is_alias_for in ["editable", "dynamic"]:
                search_expression = self.config.settings.normal_prefix + placeholder.name + self.config.settings.normal_suffix
                page_markdown = page_markdown.replace(search_expression, f"x{placeholder.name}_{self.unique}_{self.config.settings.normal_is_alias_for.upper()}x")

        return page_markdown

    def handle_html_page(self, page_html: str) -> str:
        # needs to happen in the HTML document, since otherwise listings will screw things up
        for placeholder in self.config.placeholders.values():
            page_html = page_html.replace(
                f"x{placeholder.name}_{self.unique}_DYNAMICx", html_for_dynamic_placeholder(placeholder, self.config)
            )
            page_html = page_html.replace(
                f"x{placeholder.name}_{self.unique}_EDITABLEx", html_for_editable_placeholder(placeholder, self.config)
            )

        return page_html


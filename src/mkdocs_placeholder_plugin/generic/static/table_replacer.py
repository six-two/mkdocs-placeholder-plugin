import re
# local
from ..config import PlaceholderConfig
from ..html_tag_parser import ParsedHtmlTag
from ..html_tag_handler import HtmlTagHandler
from .table_generator import TableGenerator

START_REGEX = re.compile(r'<div\s[^>]*class="?[^"]*auto-input-table', re.IGNORECASE)
END_REGEX = re.compile(r'\s*</div>', re.IGNORECASE)

class StaticHtmlElementTableFallbackReplacer(HtmlTagHandler):
    def __init__(self, config: PlaceholderConfig, add_line_in_warning: bool) -> None:
        super().__init__(START_REGEX, END_REGEX, add_line_in_warning)
        self.table_generator = TableGenerator(config)

    def replace_function(self, tag: str, parsed: ParsedHtmlTag) -> str:
        """
        If the tag is an input tag, it's value will be replaced with a warning that tells the user to enable JavaScript.
        If JavaScript is enabled, it will replace the value with the stored/default value of the placeholder.
        """
        class_names = parsed.attributes.get("class", "").split()
        if "auto-input-table" in class_names:
            used_placeholders = self.table_generator.get_placeholders_for_table(self.full_text_string)
            no_js_table = self.table_generator.generate_table_html(used_placeholders, ["TODO: add if it is used in the future"])
            return tag + no_js_table
        else:
            return tag


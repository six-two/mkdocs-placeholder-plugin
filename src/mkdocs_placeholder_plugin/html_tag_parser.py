from html.parser import HTMLParser
import os
from typing import NamedTuple, Optional
# local
from . import warning


class ParsedHtmlTag(NamedTuple):
    tag: str
    attributes: dict[str,str]


class HtmlTagParser(HTMLParser):
    """
    A generic tag parser
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.results: list[ParsedHtmlTag] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str,Optional[str]]]):
        attributes = {}
        for key, value in attrs:
            if key in attributes:
                raise Exception(f"Attribute '{key}' defined multiple times")
            else:
                attributes[key] = value or ""
        
        self.results.append(ParsedHtmlTag(tag, attributes))


def parse_html_tag(html_str: str) -> ParsedHtmlTag:
    """
    Parse the input string as a single HTML tag
    """
    parser = HtmlTagParser()
    parser.feed(html_str)
    parser.close()

    if len(parser.results) == 1:
        return parser.results[0]
    else:
        raise Exception(f"Expected one tag, but got {len(parser.results)}")


class InvalidVariableInputFieldSearcher(HTMLParser):
    """
    An HTML parser, that looks for <input> tags with data-input-for="PLACEHOLDER_NAME".
    If the given PLACEHOLDER_NAME is not defined, a warning will be issued.
    """
    def __init__(self, valid_variable_names: list[str], base_dir: str) -> None:
        super().__init__()
        self.valid_variable_names = valid_variable_names
        self.file_name = "PATH NOT SET"
        self.base_dir = base_dir

    def internal_handle_tag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        if tag == "input":
            for key, value in attrs:
                if key == "data-input-for":
                    # check if the value of the "data-input-for" attribute is a known variable
                    if value not in self.valid_variable_names:
                        warning(f"({self.file_name}) Input element is linked to non-existent variable '{value}'. Is this a typo or did you forget to set a default value for it?")

    def handle_starttag(self, tag, attrs) -> None:
        self.internal_handle_tag(tag, attrs)

    def handle_startendtag(self, tag, attrs) -> None:
        self.internal_handle_tag(tag, attrs)

    def check_file(self, path: str) -> None:
        self.file_name = os.path.relpath(path, self.base_dir)

        with open(path, "r") as f:
            html = f.read()
        self.feed(html)


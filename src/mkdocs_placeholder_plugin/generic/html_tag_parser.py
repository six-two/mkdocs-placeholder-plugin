from html.parser import HTMLParser
import html
from typing import NamedTuple, Optional


class ParsedHtmlTag(NamedTuple):
    tag: str
    attributes: dict[str,str]


def create_html_opening_tag(tag: str, attributes: dict[str,str]) -> str:
    result = "<" + tag
    for key, value in attributes.items():
        result += f' {key}="{html.escape(value)}"'
    return result + ">"


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



import re
from typing import Callable, Optional
# local
from . import warning
from .html_tag_parser import ParsedHtmlTag, parse_html_tag, create_html_opening_tag

INPUT_TAG_START = re.compile("<input", re.IGNORECASE)


class InputTagHandler:
    def __init__(self, replace_function: Callable[[str,ParsedHtmlTag],str]) -> None:
        self.replace_function = replace_function

    def process_string(self, file_name: str, html: str) -> str:
        search_start_pos = 0
        while True:
            match = INPUT_TAG_START.search(html, search_start_pos)
            if match:
                start = match.span()[0]
                end_and_parsed = find_where_tag_ends(file_name, html, start)
                if end_and_parsed:
                    end, parsed = end_and_parsed
                    old_value = html[start:end]

                    # Give the replace_function the chance to replace the part of the string
                    new_value = self.replace_function(old_value, parsed)
                    if new_value != old_value:
                        html = html[:start] + new_value + html[end:]
                    
                    # Continue searching after the end of the tag
                    search_start_pos = start + len(new_value)
                else:
                    # we cound not find out where the tag ended, so we just make sure we do not encounter it again
                    search_start_pos = start + 1
            else:
                return html
                

def find_where_tag_ends(file_name: str, html: str, start: int) -> Optional[tuple[int,ParsedHtmlTag]]:
    search_pos = start
    # Limit to small number to prevent huge performance problems if this is buggy
    for _ in range(10):
        end = html.find(">", search_pos)
        if end == -1:
            # End of string reached without finding closing tag
            break
        else:
            end += 1 # the end tag is part of the tag
            try:
                parsed = parse_html_tag(html[start:end])
                return (end, parsed)
            except:
                # Either the tag has not ended, or the it contains multiple tags
                search_pos = end
    
    # If not successful after a couple attempts, print a warning
    line_nr = html.count("\n", 0, start) + 1
    warning(f"Could not find end of tag (location={file_name}:{line_nr})")
    return None


def replace_function_set_default_value_to_js_warning(tag: str, parsed: ParsedHtmlTag) -> str:
    """
    If the tag is an input tag, it's value will be replaced with a warning that tells the user to enable JavaScript.
    If JavaScript is enabled, it will replace the value with the stored/default value of the placeholder.
    """
    placeholder_name = parsed.attributes.get("data-input-for")
    if placeholder_name:
        attrs = dict(parsed.attributes)
        attrs["value"] = "Please enable JavaScript"

        return create_html_opening_tag(parsed.tag, attrs)
    else:
        return tag


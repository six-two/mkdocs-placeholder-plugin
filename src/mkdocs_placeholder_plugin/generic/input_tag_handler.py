import re
from typing import Callable, Optional, Any
# local
from . import warning
from .html_tag_parser import ParsedHtmlTag, parse_html_tag, create_html_opening_tag

INPUT_TAG_START = re.compile("<input", re.IGNORECASE)


class InputTagHandler:
    def __init__(self, replace_function: Callable[[Any,str,ParsedHtmlTag],str], add_line_in_warning: bool) -> None:
        self.replace_function = replace_function
        # The line index may need to be disabled, if you run it aginst the HTML file
        self.add_line_in_warning = add_line_in_warning
        self.location = "Not yet initialized"

    def process_string(self, file_name: str, html: str) -> str:
        search_start_pos = 0
        while True:
            match = INPUT_TAG_START.search(html, search_start_pos)
            if match:
                start = match.span()[0]
                # Determine where we are (for useful error messages)
                if self.add_line_in_warning:
                    line_nr = html.count("\n", 0, start) + 1
                    self.location = f"{file_name}:{line_nr}"
                else:
                    self.location = file_name

                end_and_parsed = self.find_where_tag_ends(html, start)
                if end_and_parsed:
                    end, parsed = end_and_parsed
                    old_value = html[start:end]


                    # Give the replace_function the chance to replace the part of the string
                    new_value = self.replace_function(self, old_value, parsed)
                    if new_value != old_value:
                        html = html[:start] + new_value + html[end:]

                    # Continue searching after the end of the tag
                    search_start_pos = start + len(new_value)
                else:
                    # we cound not find out where the tag ended, so we just make sure we do not encounter it again
                    search_start_pos = start + 1
            else:
                return html


    def find_where_tag_ends(self, html: str, start: int) -> Optional[tuple[int,ParsedHtmlTag]]:
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
        warning(f"{self.location} - Could not find end of tag")
        return None


def create_normal_input_class_handler(placeholders: dict, add_line_in_warning: bool) -> InputTagHandler:
    def replace_function(handler, tag: str, parsed: ParsedHtmlTag) -> str:
        """
        If the tag is an input tag, it's value will be replaced with a warning that tells the user to enable JavaScript.
        If JavaScript is enabled, it will replace the value with the stored/default value of the placeholder.
        """
        placeholder_name = parsed.attributes.get("data-input-for")
        if placeholder_name:
            attrs = dict(parsed.attributes)
            # Set a value that will be shown, when the script can not run (because JS is disabled)
            attrs["value"] = "Please enable JavaScript"

            # Print a warning if the placeholder does not exist
            if placeholder_name not in placeholders:
                warning(f"{handler.location} - Input element is linked to non-existent variable '{placeholder_name}'. Is this a typo or did you forget to set a default value for it?")

            return create_html_opening_tag(parsed.tag, attrs)
        else:
            return tag

    handler = InputTagHandler(replace_function, add_line_in_warning)
    return handler

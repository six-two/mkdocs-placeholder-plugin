import re
from typing import Optional
# local
from . import warning
from .html_tag_parser import ParsedHtmlTag, parse_html_tag, create_html_opening_tag


from typing import TypeVar
# SEE: https://peps.python.org/pep-0673/
THtmlTagHandler = TypeVar("THtmlTagHandler", bound="HtmlTagHandler")

class HtmlTagHandler:
    def __init__(self, start_regex: re.Pattern, end_regex: Optional[re.Pattern], add_line_in_warning: bool) -> None:
        self.start_regex = start_regex
        self.end_regex = end_regex
        # The line index may need to be disabled, if you run it aginst the HTML file
        self.add_line_in_warning = add_line_in_warning
        self.location = "Not yet initialized"
        self.full_text_string = ""

    def replace_function(self, old_value: str, parsed: ParsedHtmlTag) -> str:
        raise Exception("You need to subclass HtmlTagHandler and overwrite the 'replace_function' method")

    def process_string(self, file_name: str, file_contents: str) -> str:
        self.full_text_string = file_contents
        search_start_pos = 0

        # replace / handle all matches
        while match := self.start_regex.search(file_contents, search_start_pos):
            file_contents, search_start_pos = self.handle_potential_occurence(file_name, file_contents, match)

        return file_contents

    def handle_potential_occurence(self, file_name: str, html: str, match: re.Match) -> tuple[str,int]:
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

            if self.end_regex and not self.end_regex.match(html[end:]):
                # End pattern does not match, so we skip it
                return (html, start + 1)
            else:
                # Only process it if no end pattern exist or if it matches
                # Give the replace_function the chance to replace the part of the string
                new_value = self.replace_function(old_value, parsed)
                if new_value != old_value:
                    html = html[:start] + new_value + html[end:]

                # Continue searching after the end of the tag
                return (html, start + len(new_value))
        else:
            # we cound not find out where the tag ended, so we just make sure we do not encounter it again
            return (html, start + 1)

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


class NormalHtmlInputElementHandler(HtmlTagHandler):
    def __init__(self, placeholders: dict, add_line_in_warning: bool) -> None:
        super().__init__(re.compile("<input", re.IGNORECASE), None, add_line_in_warning)
        self.placeholders = placeholders

    def replace_function(self, tag: str, parsed: ParsedHtmlTag) -> str:
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
            if placeholder_name not in self.placeholders:
                warning(f"{self.location} - Input element is linked to non-existent variable '{placeholder_name}'. Is this a typo or did you forget to set a default value for it?")

            return create_html_opening_tag(parsed.tag, attrs)
        else:
            return tag

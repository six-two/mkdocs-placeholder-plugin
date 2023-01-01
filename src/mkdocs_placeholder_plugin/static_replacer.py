import glob
import html
import os
import re
# local files
from . import warning
from .placeholder_data import Placeholder
from .html_tag_parser import create_html_opening_tag, ParsedHtmlTag
from .input_tag_handler import InputTagHandler

# This will fail (not match) if the placeholder name contains an space, single quote or double quote.
# But since I produce a warning on the console if you do that, that is your problem
PLACEHOLDER_INPUT_FIELD_REGEX = re.compile(r'(<input(?:\s+[^<>]*?)?)\s+data-input-for=(["\']?)([^\'"\s>]*)\2')

class StaticReplacer:
    def __init__(self, placeholders: dict[str,Placeholder], replace_file_pattern_list: list[str]) -> None:
        self.placeholders = placeholders
        self.replace_file_pattern_list = replace_file_pattern_list
        self.input_tag_modifier = create_static_input_field_replacer(placeholders)
        self.site_dir = "not yet set"

    def process_output_folder(self, folder_path: str) -> None:
        file_processed = False
        self.site_dir = folder_path
        for pattern in self.replace_file_pattern_list:
            # the iglob(root_dir=...) parameter was only introduced in 3.10, so we can not rely on it
            path_pattern = os.path.join(folder_path, pattern)
            for file_path in glob.iglob(path_pattern, recursive=True):
                file_path = os.path.relpath(file_path, folder_path)
                file_processed = True
                full_path = os.path.join(folder_path, file_path)
                self.process_file(full_path)

        if not file_processed:
            warning("Static replacements: No files were processed")

    def process_file(self, path: str) -> None:
        # @TODO: check if this causes issues with UTF-8 text (like emojis)
        # read file
        with open(path, "r") as f:
            text = f.read()
        # modify the file's contents
        text = self._replace_placeholders_in_html_page(text)
        relative_path = os.path.relpath(path, self.site_dir)
        text = self._disable_placeholder_input_fields(relative_path, text)
        # Write file
        with open(path, "w") as f:
            f.write(text)

    def _replace_placeholders_in_html_page(self, text: str) -> str:
        """
        I guess I could properly parse the page with BeautifulSoup, but that seems more complicated
        (and thus error prone) and would require extra dependenices. So I will try to just use "dumb"
        replacements and hope it does not cause any errors.
        """
        for placeholder in self.placeholders.values():
            text = text.replace(f"x{placeholder.name}x", html.escape(placeholder.default_value))
        return text

    def _disable_placeholder_input_fields(self, path: str, text: str) -> str:
        """
        Search for inputs with the data-input-for attribute and insert a disabled
        """
        return self.input_tag_modifier.process_string(path, text)


def create_static_input_field_replacer(placeholders: dict[str,Placeholder]) -> InputTagHandler:
    def static_replacer_input_tag_modifier(handler, tag: str, parsed: ParsedHtmlTag) -> str:
        placeholder_name = parsed.attributes.get("data-input-for")
        if placeholder_name:
            attrs = dict(parsed.attributes)

            # Print a warning if the placeholder does not exist
            if placeholder_name not in placeholders:
                warning(f"{handler.location} (static replacer) - Input element is linked to non-existent variable '{placeholder_name}'. Is this a typo or did you forget to set a default value for it?")
                attrs["value"] = f"Undefined variable {placeholder_name}"
            else:
                attrs["value"] = placeholders[placeholder_name].default_value
            
            # Disable the input elements
            attrs["disabled"] = "1"

            return create_html_opening_tag(parsed.tag, attrs)
        else:
            return tag
    
    return InputTagHandler(static_replacer_input_tag_modifier, False)

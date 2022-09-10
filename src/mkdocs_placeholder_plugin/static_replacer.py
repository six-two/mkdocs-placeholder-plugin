import glob
import html
import os
import re
# local files
from . import warning
from .utils import Placeholder

PLACEHOLDER_INPUT_FIELD_REGEX = re.compile(r'(<input(?:\s+[^<>]*?)?)\s+data-input-for="([^"]*)"')

class StaticReplacer:
    def __init__(self, placeholders: dict[str,Placeholder], replace_file_pattern_list: list[str]) -> None:
        self.placeholders = placeholders
        self.replace_file_pattern_list = replace_file_pattern_list

    def process_output_folder(self, folder_path: str) -> None:
        file_processed = False
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
        text = self._disable_placeholder_input_fields(text)
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
            text = text.replace(f"x{placeholder.name}x", placeholder.default_value)
        return text

    def _disable_placeholder_input_fields(self, text: str) -> str:
        """
        Search for inputs with the data-input-for attribute and insert a disabled
        """
        matches = list(PLACEHOLDER_INPUT_FIELD_REGEX.finditer(text))
        # Iterate in reverse order to not screw up the indices used when replacing text
        for match in reversed(matches):
            tag_start = match.group(1)
            placeholder_name = match.group(2)
            placeholder_value = self.placeholders[placeholder_name].default_value
            # Remove the "data-input-for" attribute (since JS may override the value) and insert a static value
            new_tag = tag_start + f' value="{html.escape(placeholder_value)}" disabled'
            start, end = match.span()
            text = text[:start] + new_tag + text[end:]

        return text

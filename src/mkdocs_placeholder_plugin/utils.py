from html.parser import HTMLParser
import os
import re
# pip packages
import yaml
# local
from . import warning

VARIABLE_NAME_REGEX = re.compile("^[A-Z_]+$")

def load_placeholder_data(path: str) -> dict[str, str]:
    """
    Load placeholder data from a file and run some checks on the parsed contents
    """
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = yaml.safe_load(f)
        
        if type(data) != dict:
            raise Exception(f"Expected 'dict', but got '{type(data)}'")
        for key, value in data.items():
            # Make sure that values are strings (or convert them to strings if possible)
            if type(value) != str:
                if type(value) in [list, dict]:
                    raise Exception(f"Expected a single value for key '{key}', but got type {type(value)}")
                else:
                    # Probably something like int, float, bool, etc
                    data[key] = str(value)
            
            # Check that the variable name matches expected format
            if not VARIABLE_NAME_REGEX.match(key):
                warning(f"Potentially problematic variable name: '{key}'. A valid name should only contain capital letters and underscores.")
        
        return data
    else:
        raise Exception(f"Placeholder data file '{path}' does not exist")


class InvalidVariableInputFieldSearcher(HTMLParser):
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

def search_for_invalid_variable_names_in_input_field_targets(search_dir: str, valid_variable_names: list[str]) -> None:
    searcher = InvalidVariableInputFieldSearcher(valid_variable_names, search_dir)
    for root, dirs, files in os.walk(search_dir):
        for name in files:
            # only check HTML files
            if name.endswith(".html"):
                path = os.path.join(root, name)
                searcher.check_file(path)

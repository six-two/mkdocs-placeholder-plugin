from html.parser import HTMLParser
import json
import os
import re
from typing import NamedTuple, Any
# pip packages
import mkdocs
import yaml
# local
from . import warning, debug

VARIABLE_NAME_REGEX = re.compile("^[A-Z_]+$")

class Placeholder(NamedTuple):
    # The name of the placeholder. For example "TEST"
    name: str
    # The default value of the placeholder. For example "123"
    default_value: str
    # The description to show when generating the input table
    description: str
    # Whether the placeholder should be protected from users editing it.
    # Use true to have hidden convenience variables. Example "COMB_EMAIL: xCOMB_FIRST_NAMEx.xCOMB_SURNAMEx@xCOMB_DOMAINx"
    read_only: bool


def load_placeholder_data(path: str) -> dict[str, Placeholder]:
    """
    Load placeholder data from a file and run some checks on the parsed contents
    """
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = yaml.safe_load(f)

        placeholders: dict[str,Placeholder] = {}
        
        if type(data) != dict:
            raise mkdocs.exceptions.PluginError(f"[placeholder] Config file error: Expected root element of type 'dict', but got '{type(data).__name__}'")
        for key, value in data.items():
            # Make sure that values are strings (or convert them to strings if possible)
            if isinstance(value, dict):
                # New style entry with attributes
                # debug(f"dict: {value}")
                placeholders[key] = parse_placeholder_dict(key, value)
            elif type(value) in [bool, float, int, str]:
                # Old config style, will only set name and default_value
                # For consistency's sake, we also parse it wit the parse_palceholder_dict() function
                # debug(f"primitive: {value}")
                placeholders[key] = parse_placeholder_dict(key, {"default": value})
            else:
                raise mkdocs.exceptions.PluginError(f"Expected a single value or object for key '{key}', but got type {type(value).__name__}")
            
            # Check that the variable name matches expected format
            if not VARIABLE_NAME_REGEX.match(key):
                warning(f"Potentially problematic variable name: '{key}'. A valid name should only contain capital letters and underscores.")
        
        return placeholders
    else:
        raise mkdocs.exceptions.PluginError(f"Placeholder data file '{path}' does not exist")


def parse_placeholder_dict(name: str, data: dict[str,Any]) -> Placeholder:
    # default (default_value) is required
    try:
        default_value = str(data["default"])
    except KeyError:
        raise mkdocs.exceptions.PluginError(f"Missing key 'default' in placeholder '{name}'")

    # Readonly is optional, defaults to False
    read_only = data.get("read_only", False)
    if type(read_only) != bool:
        raise mkdocs.exceptions.PluginError(f"Wrong type for key 'read_only' in placeholder '{name}': Expected 'bool', got '{type(read_only).__name__}'")

    # Description is optional
    description = str(data.get("description", ""))

    return Placeholder(
        name=name,
        default_value=default_value,
        description=description,
        read_only=read_only,
    )


def placeholders_to_simple_json(placeholders: dict[str, Placeholder]) -> str:
    """
    Convert the placeholders to a simple JSON sting.
    Format: {"name":"value", "another-name":"another-value", [...]}
    """
    # Convert to simple name -> value mapping
    simple_dict = {}
    for placeholder in placeholders.values():
        simple_dict[placeholder.name] = placeholder.default_value
    
    # Convert dict to JSON string
    return json.dumps(simple_dict, indent=None, sort_keys=False)


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

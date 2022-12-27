from enum import Enum, auto
from html.parser import HTMLParser
import json
import os
import re
from typing import NamedTuple, Any, Optional
# pip packages
import mkdocs
import yaml
# local
from . import warning

# Should only contain letters, numbers, and underscores (hopefully prevents them from being broken up by syntax highlighting)
# Should not begin with a number (this prevents placeholders like `1`)
# Should not begin or end with a underscore (they are reserved for internal purposes like state tracking)
VARIABLE_NAME_REGEX = re.compile("^[A-Z]([A-Z0-9_]*[A-Z0-9])?$")
# The types to accept for fields, where a string is accepted
TYPES_PRIMITIVE = [bool, float, int, str]


class ParsedHtmlTag(NamedTuple):
    tag: str
    attributes: dict[str,str]

class HtmlTagParser(HTMLParser):
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
    parser = HtmlTagParser()
    parser.feed(html_str)
    parser.close()

    if len(parser.results) == 1:
        return parser.results[0]
    else:
        raise Exception(f"Expected one tag, but got {len(parser.results)}")


class InputType(Enum):
    Field = auto()
    Checkbox = auto()
    Dropdown = auto()

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
    # For supporting advanced input fields such as dropdown menus and checkboxes
    values: dict[str,str]
    # The type is not specified directly by the user, but is instead determined from the `values` field.
    # It is stored here for internal use
    input_type: InputType


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
            elif type(value) in TYPES_PRIMITIVE:
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

    # Values are optional
    values_original: dict = data.get("values", {})
    values: dict[str,str] = {}
    for key, value in values_original.items():
        if type(value) in TYPES_PRIMITIVE:
            values[str(key)] = str(value)
        else:
            raise mkdocs.exceptions.PluginError(f"Type error in placeholder '{name}', field 'values': Expected a dictionary with primitive values, but got {value} ({type(value).__name__}) in key {key}")

    # Determine the type, and do some extra type dependent validation
    if values:
        if set(values.keys()) == {"checked", "unchecked"}:
            input_type = InputType.Checkbox
            if default_value not in ["", "checked", "unchecked"]:
                raise mkdocs.exceptions.PluginError(f"Type error in placeholder '{name}', field 'default': Allowed values for check boxes are '' (empty string), 'checked', 'unchecked'")
        else:
            input_type = InputType.Dropdown
            if default_value != "" and default_value not in values.keys():
                raise mkdocs.exceptions.PluginError(f"Type error in placeholder '{name}', field 'default': Allowed values for a dropdown box are '' (empty string), or one of the keys defined in the 'values' field")
    else:
        input_type = InputType.Field


    return Placeholder(
        name=name,
        default_value=default_value,
        description=description,
        read_only=read_only,
        values=values,
        input_type=input_type,
    )

def generate_placeholder_json(placeholders: dict[str, Placeholder]) -> str:
    placeholder_names = list(placeholders.keys())
    checkbox_data = {}
    dropdown_data = {}
    textbox_data = {}
    
    for placeholder in placeholders.values():
        if placeholder.input_type == InputType.Checkbox:
            checkbox_data[placeholder.name] = {
                "default_value": bool(placeholder.default_value == "checked"),
                "checked": placeholder.values["checked"],
                "unchecked": placeholder.values["unchecked"],
            }
        elif placeholder.input_type == InputType.Dropdown:
            # Figure out the index of the item selected by default
            default_index = 0
            for index, value in enumerate(placeholder.values.keys()):
                if placeholder.default_value == value:
                    default_index = index

            dropdown_data[placeholder.name] = {
                "default_index": default_index,
                "options": [[key, value] for key, value in placeholder.values.items()],
            }
        elif placeholder.input_type == InputType.Field:
            textbox_data[placeholder.name] = placeholder.default_value
        else:
            raise Exception(f"Unexpected input type: {placeholder.input_type}")

    result_object = {
        "checkbox": checkbox_data,
        "dropdown": dropdown_data,
        "placeholder_names": placeholder_names,
        "textbox": textbox_data,
    }
    return json.dumps(result_object, indent=None, sort_keys=False)


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

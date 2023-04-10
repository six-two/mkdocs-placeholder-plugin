from enum import Enum, auto
import re
from typing import NamedTuple, Any
# local
from .. import warning, PlaceholderConfigError
from .validator import Validator
from ..validator_functions import assert_matches_one_validator
from ..validators_predefined import VALIDATOR_PRESETS
from .parser_utils import assert_no_unknown_fields, add_problematic_data_to_exceptions, get_bool, get_string


# Should only contain letters, numbers, and underscores (hopefully prevents them from being broken up by syntax highlighting)
# Should not begin with a number (this prevents placeholders like `1`)
# Should not begin or end with a underscore (they are reserved for internal purposes like state tracking)
VARIABLE_NAME_REGEX = re.compile("^[A-Z]([A-Z0-9_]*[A-Z0-9])?$")
# The types to accept for fields, where a string is accepted
TYPES_PRIMITIVE = [bool, float, int, str]
# Only these fields are allowed in placeholders
PLACEHOLDER_FIELD_NAMES = {
    "default",
    "default-function",
    "description",
    "read_only",
    "replace_everywhere",
    "values",
    "validators",
}


class InputType(Enum):
    Field = auto()
    Checkbox = auto()
    Dropdown = auto()

class Placeholder(NamedTuple):
    """
    Stores information parsed from the placeholder file.
    """
    # The name of the placeholder. For example "TEST"
    name: str
    # The default value of the placeholder. For example "123"
    default_value: str
    # A javascript snippet to generate the default value
    default_function: str
    # The description to show when generating the input table
    description: str
    # Whether the placeholder should be protected from users editing it.
    # Use true to have hidden convenience variables. Example "COMB_EMAIL: xCOMB_FIRST_NAMEx.xCOMB_SURNAMEx@xCOMB_DOMAINx"
    read_only: bool
    # Whether to only replace visible text or to try to replace it anywhere in the DOM
    replace_everywhere: bool
    # For supporting advanced input fields such as dropdown menus and checkboxes
    values: dict[str,str]
    # The type is not specified directly by the user, but is instead determined from the `values` field.
    # It is stored here for internal use
    input_type: InputType
    # The input must conform to one of the validators. This allows mixed input such as "IPv4 address or IPv6 address or Hostname"
    validator_list: list[Validator]


@add_problematic_data_to_exceptions
def parse_placeholders(data: dict, location: str, validators: dict[str,Validator]) -> dict[str,Placeholder]:
    placeholders: dict[str,Placeholder] = {}

    if type(data) != dict:
        raise PlaceholderConfigError(f"[placeholder] Config file error: Expected root element of type 'dict', but got '{type(data).__name__}'")
    for key, value in data.items():
        # Make sure that values are strings (or convert them to strings if possible)
        if isinstance(value, dict):
            # New style entry with attributes
            # debug(f"dict: {value}")
            placeholders[key] = parse_placeholder_dict(value, f"{location}:{key}", key, validators)
        elif type(value) in TYPES_PRIMITIVE:
            # Old config style, will only set name and default_value
            # For consistency's sake, we also parse it wit the parse_palceholder_dict() function
            # debug(f"primitive: {value}")
            placeholders[key] = parse_placeholder_dict({"default": value}, f"{location}:{key}", key, validators)
        else:
            raise PlaceholderConfigError(f"Expected a single value or object for key '{key}', but got type {type(value).__name__}")

        # Check that the variable name matches expected format
        if not VARIABLE_NAME_REGEX.match(key):
            warning(f"Potentially problematic variable name: '{key}'. A valid name should only contain capital letters and underscores.")

    return placeholders


@add_problematic_data_to_exceptions
def parse_placeholder_dict(data: dict[str,Any], location: str, name: str, validators: dict[str,Validator]) -> Placeholder:
    """
    Parse a dictionary that contains the information for a single placeholder.
    """
    assert_no_unknown_fields(data, PLACEHOLDER_FIELD_NAMES)

    read_only = get_bool(data, "read_only", False)
    replace_everywhere = get_bool(data, "replace_everywhere", False)
    description = get_string(data, "description", default="")

    values = parse_values(data)
    default_value, default_function = parse_defaults(data, values)
    input_type = determine_input_type(values, default_value)
    validator_list = parse_validator_list(name, data, input_type, default_value, validators)

    return Placeholder(
        name=name,
        default_value=default_value,
        default_function=default_function,
        description=description,
        replace_everywhere=replace_everywhere,
        read_only=read_only,
        values=values,
        input_type=input_type,
        validator_list=validator_list,
    )


def parse_defaults(data: dict[str,Any], values: dict[str,str]) -> tuple[str, str]:
    # default (default_value) is required, unless values or default_function exists
    default_function = get_string(data, "default-function", default="")
    try:
        default_value = get_string(data, "default", allow_numeric=True)
        if default_function:
            raise PlaceholderConfigError("Both 'default' and 'default-function' are defined")
    except KeyError:
        default_value = ""
        if not default_function and not values:
            raise PlaceholderConfigError("Missing key 'default' or 'default-function'")
    return default_value, default_function


def parse_values(data: dict[str,Any]) -> dict[str,str]:
    # Values are optional
    values_original: dict = data.get("values", {})
    values: dict[str,str] = {}
    for key, value in values_original.items():
        if type(value) in TYPES_PRIMITIVE:
            values[str(key)] = str(value)
        else:
            raise PlaceholderConfigError(f"Field 'values': Expected a dictionary with primitive values, but got {value} ({type(value).__name__}) in key {key}")
    return values


def determine_input_type(values: dict[str,str], default_value: str) -> InputType:
    # Determine the type, and do some extra type dependent validation
    if values:
        if set(values.keys()) == {"checked", "unchecked"}:
            if default_value not in ["", "checked", "unchecked"]:
                raise PlaceholderConfigError("Field 'default': Allowed values for check boxes are '' (empty string), 'checked', 'unchecked'")
            return InputType.Checkbox
        else:
            if default_value != "" and default_value not in values.keys():
                raise PlaceholderConfigError("Field 'default': Allowed values for a dropdown box are '' (empty string), or one of the keys defined in the 'values' field")
            return InputType.Dropdown
    else:
        return InputType.Field


def parse_validator_list(placeholder_name: str, data: dict[str,Any], input_type: InputType, default_value: str, known_validators: dict[str,Validator]) -> list[Validator]:
    # Validators only exist for textboxes:
    if input_type == InputType.Field:
        if "validators" in data:
            validators = data["validators"]
            if type(validators) == str:
                validator_list = [validators]
            elif type(validators) == list:
                validator_list = validators
            else:
                raise PlaceholderConfigError(f"Field 'validators': Should be either a string or a list, but is type {type(validators).__name__}")

            # Check validator list entries
            resolved_validators: list[Validator] = []
            for validator in validator_list:
                if type(validator) == str:
                    # This is a validator preset
                    validation_preset = known_validators.get(validator)
                    if validation_preset:
                        resolved_validators.append(validation_preset)
                    else:
                        raise PlaceholderConfigError(f"No validator preset named '{validator}', valid values are: {', '.join(VALIDATOR_PRESETS)}")
                else:
                    raise PlaceholderConfigError(f"Wrong type for validator list entry: Expected 'string', got '{type(validator).__name__}'")


            if validator_list:
                assert_matches_one_validator(resolved_validators, default_value)

                duplicate_names = [x for x in validator_list if validator_list.count(x) > 1]
                if duplicate_names:
                    pretty_names_list = ", ".join(sorted(set(duplicate_names)))
                    warning(f"Placeholder {placeholder_name} has the same validator multiple times. Duplicate(s): {pretty_names_list}")

            return resolved_validators
        else:
            return []
    else:
        if "validators" in data:
            warning(f"Placeholder {placeholder_name} has field 'validators', but is not a text field. Any validators for it will be ignored.")

        return []

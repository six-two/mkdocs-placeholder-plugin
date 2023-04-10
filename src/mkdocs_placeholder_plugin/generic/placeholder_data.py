from enum import Enum, auto
import json
import os
import re
from typing import NamedTuple, Any
# pip packages
import yaml
# local
from . import warning, PlaceholderConfigError
from .validators import Validator, ValidatorRule, assert_matches_one_validator
from .validators_predefined import VALIDATOR_PRESETS
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

VALIDATOR_FIELD_NAMES = {
    "name",
    "rules",
}

VALIDATOR_RULE_FIELD_NAMES = {
    "severity",
    "regex",
    "match_function",
    "should_match",
    "error_message",
}

SEVERITY_LIST = [
    "error",
    "warn",
]

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


def load_placeholder_data(path: str) -> dict[str, Placeholder]:
    """
    Load placeholder data from a file and run some checks on the parsed contents
    """
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = yaml.safe_load(f)

        placeholders: dict[str,Placeholder] = {}

        if type(data) != dict:
            raise PlaceholderConfigError(f"[placeholder] Config file error: Expected root element of type 'dict', but got '{type(data).__name__}'")
        for key, value in data.items():
            # Make sure that values are strings (or convert them to strings if possible)
            if isinstance(value, dict):
                # New style entry with attributes
                # debug(f"dict: {value}")
                placeholders[key] = parse_placeholder_dict(value, f"{path}:{key}", key)
            elif type(value) in TYPES_PRIMITIVE:
                # Old config style, will only set name and default_value
                # For consistency's sake, we also parse it wit the parse_palceholder_dict() function
                # debug(f"primitive: {value}")
                placeholders[key] = parse_placeholder_dict({"default": value}, f"{path}:{key}", key)
            else:
                raise PlaceholderConfigError(f"Expected a single value or object for key '{key}', but got type {type(value).__name__}")

            # Check that the variable name matches expected format
            if not VARIABLE_NAME_REGEX.match(key):
                warning(f"Potentially problematic variable name: '{key}'. A valid name should only contain capital letters and underscores.")

        return placeholders
    else:
        raise PlaceholderConfigError(f"Placeholder data file '{path}' does not exist")


@add_problematic_data_to_exceptions
def parse_placeholder_dict(data: dict[str,Any], location: str, name: str) -> Placeholder:
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
    validator_list = parse_validator_list(name, data, input_type, default_value)

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


def parse_validator_list(placeholder_name: str, data: dict[str,Any], input_type: InputType, default_value: str) -> list[Validator]:
    validator_list: list[Validator] = []
    # Validators only exist for textboxes:
    if input_type == InputType.Field:
        if "validators" in data:
            validators = data["validators"]
            if type(validators) == str:
                validator_data_list = [validators]
            elif type(validators) == list:
                validator_data_list = validators
            else:
                raise PlaceholderConfigError(f"Field 'validators': Should be either a string or a list, but is type {type(validators).__name__}")

            for validator in validator_data_list:
                if type(validator) == str:
                    # This is a validator preset
                    validation_preset = VALIDATOR_PRESETS.get(validator)
                    if validation_preset:
                        validator_list.append(validation_preset)
                    else:
                        raise PlaceholderConfigError(f"No validator preset named '{validator}', valid values are: {', '.join(VALIDATOR_PRESETS)}")
                elif type(validator) == dict:
                    validator_list.append(parse_validator_object(validator, "@TODO: this will be removed anyways"))
                else:
                    raise PlaceholderConfigError(f"Wrong type for validator entry: Expected 'string' or 'dict', got '{type(validator).__name__}'")


            if validator_list:
                assert_matches_one_validator(validator_list, default_value)

                validator_names = [v.name for v in validator_list]
                duplicate_names = [x for x in validator_names if validator_names.count(x) > 1]
                if duplicate_names:
                    pretty_names_list = ", ".join(sorted(set(duplicate_names)))
                    warning(f"Placeholder {placeholder_name} has multiple validators with the same name(s). Are they redundant? Duplicate(s): {pretty_names_list}")
    else:
        if "validators" in data:
            warning(f"Placeholder {placeholder_name} has field 'validators', but is not a text field. Any validators for it will be ignored.")

    return validator_list


@add_problematic_data_to_exceptions
def parse_validator_object(data: dict[str,Any], location: str) -> Validator:
    id = get_string(data, "id")
    name = get_string(data, "name")

    rules_data = data["rules"]
    if type(rules_data) != list:
        raise PlaceholderConfigError(f"Wrong type for key 'rules_data': Expected 'list', got '{type(rules_data).__name__}'")

    if not rules_data:
        raise PlaceholderConfigError("Validators neet to have at least a rule, but received an empty list")

    rules = [parse_validator_rule(x, f"{location}[{i}]") for i, x in enumerate(rules_data)]
    return Validator(
        id=id,
        name=name,
        rules=rules,
    )


@add_problematic_data_to_exceptions
def parse_validator_rule(data: dict[str,Any], location: str) -> ValidatorRule:
    assert_no_unknown_fields(data, VALIDATOR_RULE_FIELD_NAMES)

    severity = data.get("severity", "error")
    if severity not in SEVERITY_LIST:
        raise PlaceholderConfigError(f"Unknown severity '{severity}'. Should be one of {', '.join(SEVERITY_LIST)}")

    regex = ""
    match_function = ""
    if "regex" in data:
        if "match_function" in data:
            raise PlaceholderConfigError("Keys 'regex' and 'match_function' are mutually exclusive, but both are defined")
        else:
            regex = get_string(data, "regex", allow_empty_string=False)
    else:
        if "match_function" in data:
            match_function = get_string(data, "match_function", allow_empty_string=False)
        else:
            raise PlaceholderConfigError("Missing key: you need to specify either 'regex' or 'match_function'")


    should_match = get_bool(data, "should_match")

    error_message = get_string(data, "error_message", default="")
    if not error_message:
        error_message = "Should" if should_match else "Should not"
        if regex:
            error_message += f" match the regular expression '{regex}'"
        else:
            error_message += f" return true when passed to the function '{match_function}'"

    return ValidatorRule(
        severity=severity,
        regex_string=regex,
        match_function=match_function,
        should_match=should_match,
        error_message=error_message,
    )

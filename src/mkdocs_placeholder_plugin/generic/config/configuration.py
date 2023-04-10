import os
from typing import NamedTuple
# pip packages
import yaml
# local
from .. import PlaceholderConfigError
from .parser_utils import assert_no_unknown_fields, get_bool, get_int, get_dict, add_problematic_data_to_exceptions
from .validator import Validator, parse_validators
from .placeholder import Placeholder, parse_placeholders
from ..validators_predefined import VALIDATOR_PRESETS

CONFIGURATION_FIELD_NAMES = {
    "placeholders",
    "settings",
    "validators",
}

SETTINGS_FIELD_NAMES = {
    "create_no_js_fallback",
    "debug_javascript",
    "replace_delay_millis",
    "show_warning",
}

class PlaceholderSettings(NamedTuple):
    # Whether to create static HTML fallbacks when JavaScript is not enabled
    create_no_js_fallback: bool
    # debug the javascript code
    debug_javascript: bool
    # Replace delay millis
    replace_delay_millis: int
    # Whether to show warings in the python code
    show_warnings: bool


class PlaceholderConfig(NamedTuple):
    placeholders: dict[str,Placeholder]
    settings: PlaceholderSettings
    validators: dict[str,Validator]


@add_problematic_data_to_exceptions
def parse_settings(data: dict, location: str) -> PlaceholderSettings:
    assert_no_unknown_fields(data, SETTINGS_FIELD_NAMES)

    return PlaceholderSettings(
        create_no_js_fallback=get_bool(data, "create_no_js_fallback", default=True),
        debug_javascript=get_bool(data, "debug_javascript", default=False),
        replace_delay_millis=get_int(data, "replace_delay_millis", default=0, round_float=True),
        show_warnings=get_bool(data, "show_warnings", default=True),
    )


def parse_configuration_file(path: str) -> PlaceholderConfig:
    """
    Load placeholder data from a file and run some checks on the parsed contents
    """
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = yaml.safe_load(f)

        return parse_configuration(data, path)        
    else:
        raise PlaceholderConfigError(f"Configuration file '{path}' does not exist")


@add_problematic_data_to_exceptions
def parse_configuration(data: dict, location: str) -> PlaceholderConfig:
    assert_no_unknown_fields(data, CONFIGURATION_FIELD_NAMES)

    settings_data = get_dict(data, "settings", default={})
    settings = parse_settings(settings_data, f"{location}.settings")

    validator_data = get_dict(data, "validators", default={})
    validators = parse_validators(validator_data, f"{location}.validators")

    # Clone presets and merge/overwrite them with the custom ones
    merged_validators = dict(VALIDATOR_PRESETS)
    merged_validators.update(validators)

    placeholder_data = get_dict(data, "placeholders")
    placeholders = parse_placeholders(placeholder_data, f"{location}.placeholders", merged_validators)

    return PlaceholderConfig(
        placeholders=placeholders,
        settings=settings,
        validators=merged_validators,
    )

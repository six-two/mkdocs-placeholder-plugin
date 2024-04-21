import os
from typing import NamedTuple
# pip packages
import yaml
# local
from .. import PlaceholderConfigError
from .parser_utils import assert_no_unknown_fields, get_bool, get_int, get_string, get_dict, add_problematic_data_to_exceptions
from .validator import Validator, parse_validators
from .placeholder import Placeholder, parse_placeholders

# Valid values for normal_is_alias_for
ALLOWED_REPLACE_SCHEMES = ["dynamic", "editable", "html", "static"]

CONFIGURATION_FIELD_NAMES = {
    "placeholders",
    "settings",
    "validators",
}

SETTINGS_FIELD_NAMES = {
    "auto_placeholder_tables",
    "create_no_js_fallback",
    "debug_javascript",
    "dynamic_prefix",
    "dynamic_suffix",
    "editable_prefix",
    "editable_suffix",
    "expand_auto_tables",
    "html_prefix",
    "html_suffix",
    "inline_editors",
    "normal_is_alias_for",
    "normal_prefix",
    "normal_suffix",
    "replace_delay_millis",
    "show_warnings",
    "static_prefix",
    "static_suffix",
}

class PlaceholderSettings(NamedTuple):
    apply_change_on_focus_change: bool
    auto_placeholder_tables: bool
    # Whether to create static HTML fallbacks when JavaScript is not enabled
    create_no_js_fallback: bool
    # debug the javascript code
    debug_javascript: bool
    # Default prefixes / suffixes used for different replacement methods
    dynamic_prefix: str
    dynamic_suffix: str
    editable_prefix: str
    editable_suffix: str
    expand_auto_tables: bool
    html_prefix: str
    html_suffix: str
    # default value for inline editors
    inline_editors: bool
    normal_prefix: str
    normal_suffix: str
    normal_is_alias_for: str
    # Replace delay millis
    replace_delay_millis: int
    # Whether to show warings in the python code
    show_warnings: bool
    # Default prefixes / suffixes used for different replacement methods
    static_prefix: str
    static_suffix: str

class PlaceholderConfig(NamedTuple):
    placeholders: dict[str,Placeholder]
    settings: PlaceholderSettings
    validators: dict[str,Validator]


@add_problematic_data_to_exceptions
def parse_settings(data: dict, location: str) -> PlaceholderSettings:
    assert_no_unknown_fields(data, SETTINGS_FIELD_NAMES)

    settings = PlaceholderSettings(
        apply_change_on_focus_change=get_bool(data, "apply_change_on_focus_change", default=True),
        auto_placeholder_tables=get_bool(data, "auto_placeholder_tables", default=True),
        create_no_js_fallback=get_bool(data, "create_no_js_fallback", default=True),
        debug_javascript=get_bool(data, "debug_javascript", default=False),
        dynamic_prefix=get_string(data, "dynamic_prefix", "d"),
        dynamic_suffix=get_string(data, "dynamic_suffix", "d"),
        editable_prefix=get_string(data, "editable_prefix", "e"),
        editable_suffix=get_string(data, "editable_suffix", "e"),
        expand_auto_tables=get_bool(data, "expand_auto_tables", default=True),
        html_prefix=get_string(data, "html_prefix", "i"),
        html_suffix=get_string(data, "html_suffix", "i"),
        inline_editors=get_bool(data, "inline_editors", default=True),
        normal_is_alias_for=get_string(data, "normal_is_alias_for", "editable"),
        normal_prefix=get_string(data, "normal_prefix", "x"),
        normal_suffix=get_string(data, "normal_suffix", "x"),
        replace_delay_millis=get_int(data, "replace_delay_millis", default=0, round_float=True),
        show_warnings=get_bool(data, "show_warnings", default=True),
        static_prefix=get_string(data, "static_prefix", "s"),
        static_suffix=get_string(data, "static_suffix", "s"),
    )

    # Check if the same pattern (prefix & suffix) is used by multiple replacement methods
    name = "PLACEHOLDER_NAME"
    patterns = [
        settings.dynamic_prefix + name + settings.dynamic_suffix,
        settings.editable_prefix + name + settings.editable_suffix,
        settings.html_prefix + name + settings.html_suffix,
        settings.normal_prefix + name + settings.normal_suffix,
        settings.static_prefix + name + settings.static_suffix,
    ]

    if settings.normal_is_alias_for not in ALLOWED_REPLACE_SCHEMES:
        raise PlaceholderConfigError(f"'normal_is_alias_for' has unexpected value '{settings.normal_is_alias_for}'. The allowed values are: {', '.join(ALLOWED_REPLACE_SCHEMES)}")

    if len(set(patterns)) != len(patterns):
        raise PlaceholderConfigError(f"Multiple different replacement methods search for the same pattern. The patterns are: {', '.join(patterns)}")

    return settings


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
    merged_validators = parse_validators(validator_data, f"{location}.validators")

    placeholder_data = get_dict(data, "placeholders")
    placeholders = parse_placeholders(placeholder_data, f"{location}.placeholders", merged_validators)

    return PlaceholderConfig(
        placeholders=placeholders,
        settings=settings,
        validators=merged_validators,
    )

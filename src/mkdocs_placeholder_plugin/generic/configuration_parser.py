from typing import NamedTuple
# local
from .parser_utils import assert_no_unknown_fields
from .validators import Validator
from .placeholder_data import Placeholder

SETTINGS_FIELD_NAMES = {
    "create_no_js_fallback",
}

class PlaceholderSettings(NamedTuple):
    # Whether to create static HTML fallbacks when JavaScript is not enabled
    create_no_js_fallback: bool
    # debug the javascript code
    debug_javascript: bool


class PlaceholderConfig(NamedTuple):
    settings: PlaceholderSettings
    validators: dict[str,Validator]
    placeholders: dict[str,Placeholder]


def parse_settings(data: dict) -> PlaceholderSettings:
    assert_no_unknown_fields(data, SETTINGS_FIELD_NAMES)

    raise Exception("TODO: program/resume here")

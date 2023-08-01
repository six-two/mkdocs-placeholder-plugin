from typing import Any
# local
from .. import PlaceholderConfigError
from .parser_utils import assert_no_unknown_fields, add_problematic_data_to_exceptions, get_bool, get_string, get_list
from ..validators import VALIDATOR_PRESETS, ensure_validator_presets_loaded, convert_to_proper_validators, Validator, PreValidator, ValidatorRule



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


@add_problematic_data_to_exceptions
def parse_validators(data: dict, location: str) -> dict[str,Validator]:
    custom_validators = {}

    for validator_name, validator_data in data.items():
        validator = parse_validator_object(validator_data, f"{location}.{validator_name}", validator_name)
        if validator_name in custom_validators:
            raise Exception(f"Should not be possible: User supplied validator '{validator_name}' specified twice ")
        else:
            custom_validators[validator_name] = validator

    ensure_validator_presets_loaded()
    merged_validators = dict(VALIDATOR_PRESETS)
    merged_validators.update(custom_validators)

    return convert_to_proper_validators(merged_validators)


@add_problematic_data_to_exceptions
def parse_validator_object(data: dict[str,Any], location: str, id: str) -> PreValidator:
    # id = get_string(data, "id")
    name = get_string(data, "name")

    rules_data = get_list(data, "rules", dict)
    if not rules_data:
        raise PlaceholderConfigError("Validators neet to have at least a rule, but received an empty list")

    import_rules_from = get_list(data, "import_rules_from", str, default=[])

    rules = [parse_validator_rule(x, f"{location}[{i}]") for i, x in enumerate(rules_data)]
    return PreValidator(id, name, rules, import_rules_from)


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

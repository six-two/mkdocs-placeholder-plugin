from typing import NamedTuple, Any
# local
from .. import PlaceholderConfigError
from .parser_utils import assert_no_unknown_fields, add_problematic_data_to_exceptions, get_bool, get_string


class ValidatorRule(NamedTuple):
    severity: str # warn or error
    # you need to either specify regex_string or match_function
    regex_string: str
    match_function: str
    should_match: bool
    error_message: str


class Validator:
    def __init__(self, id: str, name: str, rules: list[ValidatorRule]) -> None:
        self.id = id
        self.name = name
        self.rules = rules
        self._is_used = False

    def mark_used(self) -> None:
        self._is_used = True

    def is_used(self) -> bool:
        return self._is_used


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


def parse_validators(data: dict, location: str) -> dict[str,Validator]:
    result = {}

    for validator_name, validator_data in data.items():
        validator = parse_validator_object(validator_data, f"{location}.{validator_name}", validator_name)
        result[validator_name] = validator

    return result


@add_problematic_data_to_exceptions
def parse_validator_object(data: dict[str,Any], location: str, id: str) -> Validator:
    # id = get_string(data, "id")
    name = get_string(data, "name")

    rules_data = data["rules"]
    if type(rules_data) != list:
        raise PlaceholderConfigError(f"Wrong type for key 'rules_data': Expected 'list', got '{type(rules_data).__name__}'")

    if not rules_data:
        raise PlaceholderConfigError("Validators neet to have at least a rule, but received an empty list")

    rules = [parse_validator_rule(x, f"{location}[{i}]") for i, x in enumerate(rules_data)]
    return Validator(id, name, rules)


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

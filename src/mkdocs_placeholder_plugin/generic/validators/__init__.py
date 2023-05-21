from typing import NamedTuple
import re
# local
from .. import warning, PlaceholderConfigError


class ValidatorRule(NamedTuple):
    severity: str # warn or error
    # you need to either specify regex_string or match_function
    regex_string: str
    match_function: str
    should_match: bool
    error_message: str


class PreValidator:
    """
    Like a Validator, but it may contain references to the rules of other validators.
    Before these are resolved (by converting the object to a normal Validator), they can not be used.
    """
    def __init__(self, id: str, name: str, rules: list[ValidatorRule], import_rules_from_ids: list[str]) -> None:
        self.id = id
        self.name = name
        self.rules = rules
        self.import_rules_from_ids = import_rules_from_ids


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


VALIDATOR_PRESETS: dict[str,PreValidator] = {}

def register_validator(validator: PreValidator) -> None:
    if validator.id in VALIDATOR_PRESETS:
        raise Exception(f"[Internal error] Validator preset '{validator.id}' is defined twice")
    else:
        VALIDATOR_PRESETS[validator.id] = validator


def create_and_register_validator(id: str, name: str, first_rule: ValidatorRule, *rules: ValidatorRule) -> None:
    # We add an extra first_rule so that the typechecker can ensure that at least one rule is specified
    register_validator(PreValidator(id, name, [first_rule, *rules], []))

def create_and_register_validator_that_extends(id: str, name: str, import_rules_from: list[str], first_rule: ValidatorRule, *rules: ValidatorRule) -> None:
    # We add an extra first_rule so that the typechecker can ensure that at least one rule is specified
    register_validator(PreValidator(id, name, [first_rule, *rules], import_rules_from))


def should_match(regex_string: str, error_message: str) -> ValidatorRule:
    return ValidatorRule(
        severity="warn",
        regex_string=regex_string,
        match_function="",
        should_match=True,
        error_message=error_message,
    )

def should_not_match(regex_string: str, error_message: str) -> ValidatorRule:
    return ValidatorRule(
        severity="warn",
        regex_string=regex_string,
        match_function="",
        should_match=False,
        error_message=error_message,
    )

def must_match(regex_string: str, error_message: str) -> ValidatorRule:
    return ValidatorRule(
        severity="error",
        regex_string=regex_string,
        match_function="",
        should_match=True,
        error_message=error_message,
    )

def must_not_match(regex_string: str, error_message: str) -> ValidatorRule:
    return ValidatorRule(
        severity="error",
        regex_string=regex_string,
        match_function="",
        should_match=False,
        error_message=error_message,
    )


def ensure_validator_presets_loaded():
    # Load the classes, since they register the values on load
    from . import ip_address, internet, files

class ValidationResults(NamedTuple):
    validator_name: str
    value: str
    warnings: list[str]
    errors: list[str]


def convert_to_proper_validators(pre_validator_map: dict[str,PreValidator]) -> dict[str,Validator]:
    result = {}
    for id, pv in pre_validator_map.items():
        rules = pv.rules
        if pv.import_rules_from_ids:
            # @TODO: This implementation should just ignore dependency loops. Not sure if this is good without a warning...
            validators_to_include: dict[str,PreValidator] = {}
            _recursive_validator_include(pre_validator_map, validators_to_include, pv)
            
            rules = []
            for v in validators_to_include.values():
                rules += v.rules

            # print(pv.id, list(pv.import_rules_from_ids), list(validators_to_include)) # for debugging

            # remove duplicate rules if they exist
            rules = list(set(rules))
        result[id] = Validator(pv.id, pv.name, rules)
    return result

def _recursive_validator_include(pre_validator_map: dict[str,PreValidator], visited: dict[str,PreValidator], root: PreValidator) -> None:
    """
    Recursively visits child nodes. All visited nodes are stored in the `visited` parameter
    """
    visited[root.id] = root
    for child_id in root.import_rules_from_ids:
        if child_id not in visited:
            if child := pre_validator_map.get(child_id):
                _recursive_validator_include(pre_validator_map, visited, child)
            else:
                raise PlaceholderConfigError(f"Validator '{root.id}' has a reference to the unknown validator '{child_id}'")

def assert_matches_one_validator(validators: list[Validator], value: str) -> None:
    if not validators:
        # No validators -> Matches everything
        return

    results = [check_if_matches_validator(x, value) for x in validators]
    has_rule_without_errors = False
    for result in results:
        if not result.errors:
            if result.warnings:
                has_rule_without_errors = True
            else:
                # One of the rules matches perfectly
                return

    if has_rule_without_errors:
        # Only show the options where there are only warnings and no errors
        for result in results:
            if not result.errors:
                for msg in result.warnings:
                    warning(f"[Validation warning] '{result.value}' is no {result.validator_name}: {msg}")
    else:
        # Show all warnings and errors and raise an exception
        for result in results:
            for msg in result.errors:
                warning(f"[Validation error] '{value}' is no {result.validator_name}: {msg}")
            for msg in result.warnings:
                warning(f"[Validation warning] '{value}' is no {result.validator_name}: {msg}")
        raise PlaceholderConfigError(f"Default value '{value}' failed validation")


def check_if_matches_validator(validator: Validator, default_value: str) -> ValidationResults:
    warnings = []
    errors = []
    for rule in validator.rules:
        if rule.regex_string:
            try:
                matches = bool(re.search(rule.regex_string, default_value))
            except Exception as ex:
                raise PlaceholderConfigError(f"Error in regular expression '{rule.regex_string}': {ex}")

            if matches != rule.should_match:
                # This rule fails
                if rule.severity == "error":
                    errors.append(rule.error_message)
                elif rule.severity == "warn":
                    warnings.append(rule.error_message)
                else:
                    raise PlaceholderConfigError(f"Unexpected severity: '{rule.severity}'")
        else:
            # We can not really check the custom JavaScript function at build time.
            # Do we just assume that everything is ok.
            pass

    return ValidationResults(
        validator_name=validator.name,
        value=default_value,
        warnings=warnings,
        errors=errors,
    )



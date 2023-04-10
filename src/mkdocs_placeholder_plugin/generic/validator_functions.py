from typing import NamedTuple
import re
# local
from . import warning, PlaceholderConfigError
from .config import Validator, ValidatorRule


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


class ValidationResults(NamedTuple):
    validator_name: str
    value: str
    warnings: list[str]
    errors: list[str]


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



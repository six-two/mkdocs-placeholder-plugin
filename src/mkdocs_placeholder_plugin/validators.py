from typing import NamedTuple
from mkdocs.exceptions import PluginError
import re
# local
from . import warning

class ValidatorRule(NamedTuple):
    severity: str # warn or error
    # you need to either specify regex_string or match_function
    regex_string: str
    match_function: str
    should_match: bool
    error_message: str

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


class Validator(NamedTuple):
    name: str
    rules: list[ValidatorRule]


def validator_to_dict(v: Validator) -> dict:
    try:
        return {
            "name": v.name,
            "rules": [validator_rule_to_dict(r) for r in v.rules],
        }
    except Exception as ex:
        raise PluginError(f"Error while converting validator '{v.name}' to dictionary: {ex}")

def validator_rule_to_dict(r: ValidatorRule) -> dict:
    data = {
        "severity": r.severity,
        "should_match": r.should_match,
        "error_message": r.error_message,
    }
    if r.match_function:
        if r.regex_string:
            raise PluginError(f"Error in rule: 'match_function' ({r.match_function}) and 'regex_string' ({r.regex_string}) are mutually exclusive, but both are defined")
        else:
            data["match_function"] = r.match_function
    else:
        if r.regex_string:
            data["regex"] = r.regex_string
        else:
            raise PluginError("Error in rule: You need to either specify 'match_function' or 'regex_string', but both are empty")
    
    return data

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
        raise PluginError(f"Default value '{value}' failed validation")


def check_if_matches_validator(validator: Validator, default_value: str) -> ValidationResults:
    warnings = []
    errors = []
    for rule in validator.rules:
        if rule.regex_string:
            try:
                matches = bool(re.search(rule.regex_string, default_value))
            except Exception as ex:
                raise PluginError(f"Error in regular expression '{rule.regex_string}': {ex}")

            if matches != rule.should_match:
                # This rule fails
                if rule.severity == "error":
                    errors.append(rule.error_message)
                elif rule.severity == "warn":
                    warnings.append(rule.error_message)
                else:
                    raise PluginError(f"Unexpected severity: '{rule.severity}'")
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



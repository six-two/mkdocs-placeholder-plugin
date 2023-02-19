from typing import NamedTuple

class ValidatorRule(NamedTuple):
    severity: str # warn or error
    regex_string: str
    should_match: bool
    error_message: str

def should_match(regex_string: str, error_message: str) -> ValidatorRule:
    return ValidatorRule(
        severity="warn",
        regex_string=regex_string,
        should_match=True,
        error_message=error_message,
    )

def must_match(regex_string: str, error_message: str) -> ValidatorRule:
    return ValidatorRule(
        severity="error",
        regex_string=regex_string,
        should_match=True,
        error_message=error_message,
    )


class Validator(NamedTuple):
    name: str
    rules: list[ValidatorRule]


def validator_to_dict(v: Validator) -> dict:
    return {
        "name": v.name,
        "rules": [validator_rule_to_dict(r) for r in v.rules],
    }

def validator_rule_to_dict(r: ValidatorRule) -> dict:
    return {
        "severity": r.severity,
        "regex": r.regex_string,
        "should_match": r.should_match,
        "error_message": r.error_message,
    }



def generate_ipv4_validator() -> Validator:
    byte_regex = "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
    return Validator(
        name="IPv4 address",
        rules=[
            must_match("^[0-9.]+$", "Only numbers and dots are allowed"),
            # There are other ways of specifying IP addresses, that not all software understands. For example: 2130706433, 017700000001, and 127.1 are alternative representations of 127.0.0.1
            # So we just filter for expected characters, but not for the pattern
            should_match(f"^{byte_regex}(?:\\.{byte_regex}){{3}}$", "Expected an value like 123.4.56.78"),
        ]
    )


def generate_port_validator() -> Validator:
    port_regex="^((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$"
    return Validator(
        name="TCP/UDP port",
        rules=[
            must_match("^[0-9]+$", "Only numbers are allowed"),
            should_match(port_regex, "Expected an number between 0 and 65535 (inclusive)"),
        ]
    )

RULE_DOMAIN_CHARS = must_match("^[a-zA-Z0-9-.]+$", "Only letters, numbers, dashes (minus signs), and dots are allowed")
RULE_DOMAIN_START = must_match("^[^.-]", "Can not begin with a dot or dash (minus sign)")
RULE_DOMAIN_END = must_match("[^.-]$", "Can not end with a dot or dash (minus sign)")
RULE_DOMAIN_LENGTH = should_match("^([a-zA-Z0-9-]{1,63}\\.)+[a-zA-Z0-9-]{1,63}$", "Subdomains should not be longer than 63 characters")

def generate_domain_name_validator() -> Validator:
    return Validator(
        name="Domain name",
        rules=[
            RULE_DOMAIN_CHARS, RULE_DOMAIN_START, RULE_DOMAIN_END, RULE_DOMAIN_LENGTH,
            should_match("\\.", "Should contain multiple elements (for example domain.com or my.domain.com)"),
        ]
    )

def generate_hostname_validator() -> Validator:
    return Validator(
        name="Hostname",
        rules=[
            RULE_DOMAIN_CHARS, RULE_DOMAIN_START, RULE_DOMAIN_END, RULE_DOMAIN_LENGTH
        ]
    )


VALIDATOR_PRESETS = {
    "ipv4_address": generate_ipv4_validator(),
    "port_number": generate_port_validator(),
    "domain": generate_domain_name_validator(),
    "hostname": generate_hostname_validator(),
}

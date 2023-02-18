from typing import NamedTuple

class ValidatorPreset(NamedTuple):
    # This can be used to set hard boundaries, so that values do not break/hijack commands if they are used in them (at least while I have not implemented output escaping)
    # This is the regex that a value MUST match, otherwise it will not be accepted
    must_match_regex: str
    # This message will be shown, when the value is rejected
    must_match_message: str

    # This can be used to warn users, when they likely made an error. So you can use a very strict pattern, without breaking the app if the user needs a value that does not match
    # This is the regex, that the value should match. It will still be accepted, but a warning will be shown
    should_match_regex: str
    # This message will be shown, when the value does not match the should_match_regex pattern
    should_match_message: str

def generate_ipv4_validator() -> ValidatorPreset:
    byte_regex = "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"

    return ValidatorPreset(
        must_match_regex="^[0-9.]+$",
        must_match_message="Only numbers and dots are allowed in IPv4 addresses",
        # There are other ways of specifying IP addresses, that not all software understands. For example: 2130706433, 017700000001, and 127.1 are alternative representations of 127.0.0.1
        # So we just filter for expected characters, but not for the pattern
        should_match_regex=f"^{byte_regex}(?:\\.{byte_regex}){{3}}$",
        should_match_message="Expected an IPv4 address like 123.4.56.78"
    )

def generate_port_validator() -> ValidatorPreset:
    return ValidatorPreset(
        # Source: https://ihateregex.io/expr/port/
        must_match_regex="^((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$",
        must_match_message="Port number must be an positive integer between 0 and 65535 (inclusive)",
        # There are other ways of specifying IP addresses, that not all software understands. For example: 2130706433, 017700000001, and 127.1 are alternative representations of 127.0.0.1
        # So we just filter for expected characters, but not for the pattern
        should_match_regex="",
        should_match_message=""
    )


VALIDATOR_PRESETS = {
    "ipv4_address": generate_ipv4_validator(),
    "port_number": generate_port_validator(),
}

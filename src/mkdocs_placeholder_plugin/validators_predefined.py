# local
from .validators import Validator, must_match, must_not_match, should_match, should_not_match

IPV4_SEGMENT = "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
IPV4_ADDRESS = f"{IPV4_SEGMENT}(?:\\.{IPV4_SEGMENT}){{3}}"
CIDR_SUFFIX = "/(3[0-2]|[12]?[0-9])"
URL_REGEX = "[a-zA-Z0-9-]+://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+(#\S*)?"
RULE_URL_NO_WHITESPACE = must_not_match("\s", "URLs may not contain whitespace. Please URL encode it. For example a space should be replaced with '%20'")


def generate_url_http_validator() -> Validator:
    # source: https://urlregex.com. Modified to handle the fragment part (what comes after #)
    return Validator(
        name="URL (HTTP / HTTPS)",
        rules=[
            must_match("^https?://", "Needs to start with 'http://' or 'https://'"),
            RULE_URL_NO_WHITESPACE,
            should_match(f"^{URL_REGEX}$", "Expected an value like https://example.com/some/page.php?x=1&y=some%20value"),
        ]
    )

def generate_url_validator() -> Validator:
    # source: https://urlregex.com. Modified to handle the fragment part (what comes after #)
    return Validator(
        name="URL (any protocol)",
        rules=[
            RULE_URL_NO_WHITESPACE,
            should_match(f"^{URL_REGEX}$", "Expected an value like smb://example.com:10445/share/some-file.txt"),
        ]
    )


def generate_ipv4_validator() -> Validator:
    return Validator(
        name="IPv4 address",
        rules=[
            must_match("^[0-9.]+$", "Only numbers and dots are allowed"),
            # There are other ways of specifying IP addresses, that not all software understands. For example: 2130706433, 017700000001, and 127.1 are alternative representations of 127.0.0.1
            # So we just filter for expected characters, but not for the pattern
            should_match(f"^{IPV4_ADDRESS}$", "Expected an value like 123.4.56.78"),
        ]
    )

def generate_ipv4_range_cidr_validator() -> Validator:
    return Validator(
        name="IPv4 adress range (CIDR notation)",
        rules=[
            must_match("^[0-9./]+$", "Only numbers, dots and a slash are allowed"),
            must_not_match("/.*/", "May only contain one slash"),
            must_match(f"{CIDR_SUFFIX}$", "The number after that slash needs to be between 0 and 32 (inclusive)"),
            # There are other ways of specifying IP addresses, that not all software understands. For example: 2130706433, 017700000001, and 127.1 are alternative representations of 127.0.0.1
            # So we just filter for expected characters, but not for the pattern
            should_match(f"^{IPV4_ADDRESS}/[0-9]+$", "Expected an value like 123.4.56.0/24"),
        ]
    )


def generate_ipv4_range_dash_validator() -> Validator:
    IPV4_SEGMENT_DASH = f"{IPV4_SEGMENT}(-{IPV4_SEGMENT})?"
    IPV4_ADDRESS_DASHES = f"{IPV4_SEGMENT_DASH}(?:\\.{IPV4_SEGMENT_DASH}){{3}}"
    return Validator(
        name="IPv4 adress range (dash)",
        rules=[
            must_match("^[0-9-.]+$", "Only numbers, dots and minuses are allowed"),
            must_not_match("(-\.|\.-)", "Number should be on both sites of the dash"),
            must_not_match("--", "Consecutive dashes are not allowed"),
            # There are other ways of specifying IP addresses, that not all software understands. For example: 2130706433, 017700000001, and 127.1 are alternative representations of 127.0.0.1
            # So we just filter for expected characters, but not for the pattern
            should_match(f"^{IPV4_ADDRESS_DASHES}$", "Expected an value like 123.4-5.56.78-90"),
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
RULE_DOMAIN_LENGTH = should_not_match("[a-zA-Z0-9-]{64}", "Subdomains should not be longer than 63 characters")

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
    "domain": generate_domain_name_validator(),
    "hostname": generate_hostname_validator(),
    "ipv4_address": generate_ipv4_validator(),
    "ipv4_range_cidr": generate_ipv4_range_cidr_validator(),
    "ipv4_range_dashes": generate_ipv4_range_dash_validator(),
    "port_number": generate_port_validator(),
    "url_any": generate_url_validator(),
    "url_http": generate_url_http_validator(),
}
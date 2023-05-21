# local
from . import must_match, must_not_match, should_match, should_not_match, create_and_register_validator


RULE_DOMAIN_CHARS = must_match("^[a-zA-Z0-9-.]+$", "Only letters, numbers, dashes (minus signs), and dots are allowed")
RULE_DOMAIN_START = must_match("^[^.-]", "Can not begin with a dot or dash (minus sign)")
RULE_DOMAIN_END = must_match("[^.-]$", "Can not end with a dot or dash (minus sign)")
RULE_DOMAIN_LENGTH = should_not_match("[a-zA-Z0-9-]{64}", "Subdomains should not be longer than 63 characters")

RULE_URL_NO_WHITESPACE = must_not_match(r"\s", "URLs may not contain whitespace. Please URL encode it. For example a space should be replaced with '%20'")
# source: https://urlregex.com. Modified to handle the fragment part (what comes after #)
URL_REGEX = r"[a-zA-Z0-9-]+://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+(#\S*)?"
PORT_REGEX = r"^((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$"

#@TODO: extend notation?
create_and_register_validator(
    "domain",
    "Domain name",
    RULE_DOMAIN_CHARS,
    RULE_DOMAIN_START,
    RULE_DOMAIN_END,
    RULE_DOMAIN_LENGTH,
    should_match("\\.", "Should contain multiple elements (for example domain.com or my.domain.com)"),
)

create_and_register_validator(
    "hostname",
    "Hostname",
    RULE_DOMAIN_CHARS,
    RULE_DOMAIN_START,
    RULE_DOMAIN_END,
    RULE_DOMAIN_LENGTH,
)

create_and_register_validator(
    "url_any",
    "URL (any protocol)",
    RULE_URL_NO_WHITESPACE,
    should_match(f"^{URL_REGEX}$", "Expected an value like smb://example.com:10445/share/some-file.txt"),
)

create_and_register_validator(
    "port_number",
    "TCP/UDP port",
    must_match("^[0-9]+$", "Only numbers are allowed"),
    should_match(PORT_REGEX, "Expected an number between 0 and 65535 (inclusive)"),
)

create_and_register_validator(
    "url_http",
    "URL (HTTP / HTTPS)",
    must_match("^https?://", "Needs to start with 'http://' or 'https://'"),
    RULE_URL_NO_WHITESPACE,
    should_match(f"^{URL_REGEX}$", "Expected an value like https://example.com/some/page.php?x=1&y=some%20value"),
)


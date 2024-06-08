# local
from . import must_match, must_not_match, should_match, should_not_match, create_and_register_validator

CIDR_SUFFIX = "/(3[0-2]|[12]?[0-9])"
IPV4_SEGMENT = "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
IPV4_ADDRESS = f"{IPV4_SEGMENT}(?:\\.{IPV4_SEGMENT}){{3}}"
IPV4_SEGMENT_DASH = f"{IPV4_SEGMENT}(-{IPV4_SEGMENT})?"
IPV4_ADDRESS_DASHES = f"{IPV4_SEGMENT_DASH}(?:\\.{IPV4_SEGMENT_DASH}){{3}}"

# Source: https://ihateregex.io/expr/ipv6/
# Not great, does not match that well
MEDIOCRE_IPV6_REGEX = r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"


create_and_register_validator(
    "ipv6_address",
    "IPv6 address",
    must_match("^[0-9a-fA-F:.\\[\\]]+$", "Only numbers, the letters A-F, colons, dots, and square brackets are allowed"),
    should_match(f"^{MEDIOCRE_IPV6_REGEX}$", "Should probably look like '2001:0db8:85a3:0000:0000:8a2e:0370:7334' or '::1'"),
    should_not_match(f"^{IPV4_ADDRESS}$", "Should not be an IPv4 address. If you want a IPv4-mapped IPv6 address, prefix it with '::FFFF:' like this: '::FFFF:123.4.56.78'"),
)


create_and_register_validator(
    "ipv4_address",
    "IPv4 address",
    must_match("^[0-9.]+$", "Only numbers and dots are allowed"),
    # There are other ways of specifying IP addresses, that not all software understands. For example: 2130706433, 017700000001, and 127.1 are alternative representations of 127.0.0.1
    # So we just filter for expected characters, but not for the pattern
    should_match(f"^{IPV4_ADDRESS}$", "Expected an value like 123.4.56.78"),
)

create_and_register_validator(
    "ipv4_range_cidr",
    "IPv4 adress range (CIDR notation)",
    must_match("^[0-9./]+$", "Only numbers, dots and a slash are allowed"),
    must_not_match("/.*/", "May only contain one slash"),
    must_match(f"{CIDR_SUFFIX}$", "The number after that slash needs to be between 0 and 32 (inclusive)"),
    # There are other ways of specifying IP addresses, that not all software understands. For example: 2130706433, 017700000001, and 127.1 are alternative representations of 127.0.0.1
    # So we just filter for expected characters, but not for the pattern
    should_match(f"^{IPV4_ADDRESS}/[0-9]+$", "Expected an value like 123.4.56.0/24"),
)

create_and_register_validator(
    "ipv4_range_dashes",
    "IPv4 adress range (dash)",
    must_match("^[0-9-.]+$", "Only numbers, dots and minuses are allowed"),
    must_not_match(r"(-\.|\.-|^-|-$)", "Number should be on both sites of the dash"),
    must_not_match("--", "Consecutive dashes are not allowed"),
    # There are other ways of specifying IP addresses, that not all software understands. For example: 2130706433, 017700000001, and 127.1 are alternative representations of 127.0.0.1
    # So we just filter for expected characters, but not for the pattern
    should_match(f"^{IPV4_ADDRESS_DASHES}$", "Expected an value like 123.4-5.56.78-90"),
)

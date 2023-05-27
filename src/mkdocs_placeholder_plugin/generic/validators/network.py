# local
from . import must_match, must_not_match, should_match, should_not_match, create_and_register_validator, MUST_NOT_BE_EMPTY

# @TODO new validators: number, linux username

# @SOURCE: https://ihateregex.io/expr/mac-address/
MAC_PATTERN = r"^[a-fA-F0-9]{2}(:[a-fA-F0-9]{2}){5}$"

# @SOURCE: https://ihateregex.io/expr/uuid/
UUID_PATTERN = r"^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$"

create_and_register_validator(
    "uuid", 
    "UUID",
    must_match(UUID_PATTERN, "Should look like '123e4567-e89b-12d3-a456-426614174000'"),
    must_not_match("[^0-9a-fA-F-]", "Can only contain hexadecimal digits and hyphens"),
)

create_and_register_validator(
    "linux_interface",
    "Linux network interface",
    should_match("^[a-z0-9-_]$", "Should only contain lowercase letters, numbers, underscores, and dashes"),
    MUST_NOT_BE_EMPTY,
)

create_and_register_validator(
    "mac_address",
    "MAC address",
    must_match(MAC_PATTERN, "Should look like '01:23:45:67:89:AB'"),
)

create_and_register_validator(
    "email",
    "Email address",
    must_match("^[^@]*@[^@]*$", "Must contain exactly one '@' character"),
    must_match("@[a-zA-Z0-9-.]+$", "Only letters, numbers, dashes (minus signs), and dots are allowed after the @ sign"),
    must_match(r"@.+\...+", "Must have a full domain (like 'gmail.com') after the at sign"),
    must_not_match(r"\s", "Can not contain whitespace"),
)

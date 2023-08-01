# local
from . import must_not_match, should_not_match, create_and_register_validator, create_and_register_validator_that_extends, MUST_NOT_BE_EMPTY

RULE_WINDOS_NAME_PROHIBITED = must_not_match('[<>:"|?*]', 'Can not contain prohibited characters: \'<>:"|?*\'')
RULE_WARN_WHITESPACE = should_not_match(r"\s", "Should not contain whitespace")


create_and_register_validator_that_extends(
    "file_name_linux",
    "File name",
    ["path_linux"],
    must_not_match(r"/", "Can not contain path separators (slash)"),
)

create_and_register_validator_that_extends(
    "file_name_windows",
    "File name",
    ["path_windows"],
    must_not_match(r"[/\\]", "Can not contain path separators (slash or backslash)"),
)

create_and_register_validator(
    "path_linux",
    "File path (Linux)",
    MUST_NOT_BE_EMPTY,
    RULE_WARN_WHITESPACE,
)

create_and_register_validator(
    "path_windows",
    "File path (Windows)",
    MUST_NOT_BE_EMPTY,
    # Colon may be in 'C:\...' (and maybe for a port number in an UNC path?)
    should_not_match('[<>"|?*]', 'Can not contain prohibited characters: \'<>"|?*\''),
    RULE_WARN_WHITESPACE,
)

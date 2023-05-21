# local
from . import must_match, must_not_match, should_match, should_not_match, create_and_register_validator

RULE_NOT_EMPTY = must_match("^.+$", "Can not be empty")
RULE_WINDOS_NAME_PROHIBITED = must_not_match('[<>:"|?*]', 'Can not contain prohibited characters: \'<>:"|?*\'')
RULE_WARN_WHITESPACE = should_not_match(r"\s", "Should not contain whitespace")


create_and_register_validator(
    "file_name_linux",
    "File name",
    RULE_NOT_EMPTY,
    must_not_match("/", "Can not contain path separators (slash)"),
    RULE_WARN_WHITESPACE,
)

create_and_register_validator(
    "file_name_windows",
    "File name",
    RULE_NOT_EMPTY,
    must_not_match(r"[/\\]", "Can not contain path separators (slash or backslash)"),
    must_not_match('[<>:"|?*]', 'Can not contain prohibited characters: \'<>:"|?*\''),
    RULE_WARN_WHITESPACE,
)

create_and_register_validator(
    "path_linux",
    "File path (Linux)",
    RULE_NOT_EMPTY,
    RULE_WARN_WHITESPACE,
)

create_and_register_validator(
    "path_windows",
    "File path (Windows)",
    RULE_NOT_EMPTY,
    # Colon may be in 'C:\...' (and maybe for a port number in an UNC path?)
    should_not_match('[<>"|?*]', 'Can not contain prohibited characters: \'<>"|?*\''),
    RULE_WARN_WHITESPACE,
)

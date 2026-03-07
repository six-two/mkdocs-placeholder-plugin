# local
from . import must_match, must_not_match, should_not_match, create_and_register_validator


create_and_register_validator(
    "int",
    "Integer",
    must_match("^[+-]?[0-9]+$", "Only integers are allowed"),
    should_not_match("^[0-9]{11}", "Your number is very big, this could cause problems"),
)

create_and_register_validator(
    "uint",
    "Positive integer",
    must_match("^[+-]?[0-9]+$", "Only positive integers are allowed"),
    must_not_match("^-", "Negative numbers are not allowed"),
    should_not_match("^[0-9]{11}", "Your number is very big, this could cause problems"),
)

create_and_register_validator(
    "float",
    "Floating point number",
    # From https://regex101.com/r/f8aZCF/1
    must_match(r"^[+-]?((\d+(\.\d*)?)|((\d*\.\d+)))(e[-+]?\d*)?$", "Only floating point numbers (including e notation) are allowed"),
)

create_and_register_validator(
    "ufloat",
    "Positive floating point number",
    # From https://regex101.com/r/f8aZCF/1
    must_match(r"^[+-]?((\d+(\.\d*)?)|((\d*\.\d+)))(e[-+]?\d*)?$", "Only floating point numbers (including e notation) are allowed"),
    must_not_match("^-", "Negative numbers are not allowed"),
)


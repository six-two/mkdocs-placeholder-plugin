from functools import wraps
import json
from typing import Callable, Optional
# local
from . import PlaceholderConfigError

class PlaceholderConfigErrorWithData(PlaceholderConfigError):
    """
    Config exception that already has data of what caused it appended.
    This makes finding the error in your configuration much easier.
    """
    def __init__(self, message: str, location: str, data: dict) -> None:
        # Immediately create a string out of the data, since it might be changed afterwards
        super().__init__(f"{message}\n\nCaused by data at {location}: {json.dumps(data, indent=4)}")
        self.error_location = location
        self.error_data = data

def assert_no_unknown_fields(data: dict, known_field_names: set[str]) -> None:
    unexpected_fields = set(data).difference(known_field_names)
    if unexpected_fields:
        raise PlaceholderConfigError(f"Unexpected field(s): {', '.join(unexpected_fields)}")

def add_problematic_data_to_exceptions(function: Callable) -> Callable:
    @wraps(function)
    def wrap(data: dict, location: str, *args, **kwargs):
        try:
            return function(data, location, *args, **kwargs)
        except PlaceholderConfigErrorWithData:
            # This already has more detailed data, so we just reraise it.
            # Otherwise you might have a bunch of useles exceptions in the chain adding bigger and bigger JSON dumps,
            # which makes it harder to find the actual root cause
            raise
        except Exception as ex:
            message = f"Missing key {ex}" if type(ex) == KeyError else str(ex)
            raise PlaceholderConfigErrorWithData(message, location, data)
    return wrap


def get_bool(data: dict, name: str, default: Optional[bool] = None) -> bool:
    """
    Reads the given key from data. If no value is used, default is used.
    If default is None/not set then a KeyError will be thrown
    """
    if default == None:
        value = data[name]
    else:
        value = data.get(name, default)

    if type(value) == bool:
        return value
    else:
        raise PlaceholderConfigError(f"Wrong type for key '{name}': Expected 'bool', got '{type(value).__name__}'")


def get_string(data: dict, name: str, default: Optional[str] = None, allow_empty_string: bool = True, allow_numeric: bool = False) -> str:
    """
    Reads the given key from data. If no value is used, default is used.
    If default is None/not set then a KeyError will be thrown
    """
    if default == None:
        value = data[name]
    else:
        value = data.get(name, default)

    if type(value) == str:
        if allow_empty_string or value:
            return value
        else:
            raise PlaceholderConfigError(f"Invalid value for key '{name}': Can not be an empty string")
    elif type(value) == int or type(value) == float:
        if allow_numeric:
            return str(value)
        else:
            raise PlaceholderConfigError(f"Wrong type for key '{name}': Expected 'str', but got a number. Try surrounding it with quotes or modify the code and set 'allow_numeric=true'")
    else:
        raise PlaceholderConfigError(f"Wrong type for key '{name}': Expected 'str', got '{type(value).__name__}'")

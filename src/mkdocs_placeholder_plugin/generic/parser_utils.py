from functools import wraps
import json
from typing import Callable
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

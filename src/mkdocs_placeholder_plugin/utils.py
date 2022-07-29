import os
import re
# pip packages
import yaml
# local
from . import warning

VARIABLE_NAME_REGEX = re.compile("^[A-Z_]+$")

def load_placeholder_data(path: str) -> dict[str, str]:
    """
    Load placeholder data from a file and run some checks on the parsed contents
    """
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = yaml.safe_load(f)
        
        if type(data) != dict:
            raise Exception(f"Expected 'dict', but got '{type(data)}'")
        for key, value in data.items():
            # Make sure that values are strings (or convert them to strings if possible)
            if type(value) != str:
                if type(value) in [list, dict]:
                    raise Exception(f"Expected a single value for key '{key}', but got type {type(value)}")
                else:
                    # Probably something like int, float, bool, etc
                    data[key] = str(value)
            
            # Check that the variable name matches expected format
            if not VARIABLE_NAME_REGEX.match(key):
                warning(f"Potentially problematic variable name: '{key}'. A valid name should only contain capital letters and underscores.")
        
        return data
    else:
        raise Exception(f"Placeholder data file '{path}' does not exist")


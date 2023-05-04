import os
import shutil
from typing import Optional
# local
from ..generic.config import PlaceholderConfig
from ..generic.json_generator import generate_json_for_javascript_code

COMBINED_FILE_NAME = "placeholder-combined.js"
DEBUGGABLE_CODE_FILE_NAME = "placeholder.min.js"
DEBUGGABLE_DATA_FILE_NAME = "placeholder-data.js"


def copy_assets_to_directory_combined(generic_config: PlaceholderConfig, output_directory: str, optional_custom_script_path: Optional[str]):
    os.makedirs(output_directory, exist_ok=True)

    library_code = read_resource_file(DEBUGGABLE_CODE_FILE_NAME)
    # Remove the ling to the source map, since the file is not copied / would not fit due too the extra code that is prepended
    library_code = library_code.replace(f"//# sourceMappingURL={DEBUGGABLE_CODE_FILE_NAME}.map", "")

    if optional_custom_script_path:
        with open(optional_custom_script_path, "r") as f:
            extra_js = f.read()
        custom_code = f"///// Custom extra JS code /////\n{extra_js}\n\n\n"
    else:
        custom_code = "///// No custom extra JS code exists /////\n"

    json_data = generate_json_for_javascript_code(generic_config)
    data_code = f"window.PlaceholderPluginConfigJson = {json_data};"

    # Combine the different files and store the results in the output directory
    combined_code = f"{custom_code}///// Plugin data /////\n{data_code}\n\n\n///// Normal plugin code /////\n{library_code}\n\n\n"
    output_file = os.path.join(output_directory, COMBINED_FILE_NAME)
    with open(output_file, "w") as f:
        f.write(combined_code)


def copy_assets_to_directory_debuggable(generic_config: PlaceholderConfig, output_directory: str, optional_custom_script_path: Optional[str]):
    os.makedirs(output_directory, exist_ok=True)

    # copy files
    shutil.copy(get_resource_path(DEBUGGABLE_CODE_FILE_NAME), output_directory)
    shutil.copy(get_resource_path(f"{DEBUGGABLE_CODE_FILE_NAME}.map"), output_directory)

    data_code = read_resource_file(DEBUGGABLE_DATA_FILE_NAME)

    # Replace placeholder
    json_data = generate_json_for_javascript_code(generic_config)
    data_code = data_code.replace("__MKDOCS_PLACEHOLDER_PLUGIN_NEW_JSON__", json_data)

    if optional_custom_script_path:
        with open(optional_custom_script_path, "r") as f:
            extra_js = f.read()

        data_code = "///// Custom extra JS code /////\n" + extra_js + "\n\n\n///// Plugin data /////\n" + data_code

    data_output_file = os.path.join(output_directory, DEBUGGABLE_DATA_FILE_NAME)
    with open(data_output_file, "w") as f:
        f.write(data_code)


def read_resource_file(name: str) -> str:
    path = get_resource_path(name)
    with open(path, "r") as f:
        return f.read()



def get_resource_path(name: str) -> str:
    """
    Gets the path to a file in the same directory as this file
    """
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, name)


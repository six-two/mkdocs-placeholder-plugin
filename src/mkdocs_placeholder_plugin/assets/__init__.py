import os
import shutil
from typing import Optional
# local
from ..generic.config import PlaceholderConfig
from ..generic.json_generator import generate_json_for_javascript_code


def copy_assets_to_directory_debuggable(generic_config: PlaceholderConfig, output_directory: str, optional_custom_script_path: Optional[str]):
    os.makedirs(output_directory, exist_ok=True)

    shutil.copy(get_resource_path("placeholder.min.js"), output_directory)
    shutil.copy(get_resource_path("placeholder.min.js.map"), output_directory)

    input_file = get_resource_path("placeholder-data.js")
    json_data = generate_json_for_javascript_code(generic_config)
    with open(input_file, "r") as f:
        text = f.read().replace("__MKDOCS_PLACEHOLDER_PLUGIN_NEW_JSON__", json_data)

    if (optional_custom_script_path):
        with open(optional_custom_script_path, "r") as f:
            extra_js = f.read()

        text = "///// Custom extra JS code /////\n" + extra_js + "\n\n\n///// Plugin's JS code /////\n" + text

    data_output_file = os.path.join(output_directory, "placeholder-data.js")
    with open(data_output_file, "w") as f:
        f.write(text)


def get_resource_path(name: str) -> str:
    """
    Gets the path to a file in the same directory as this file
    """
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, name)


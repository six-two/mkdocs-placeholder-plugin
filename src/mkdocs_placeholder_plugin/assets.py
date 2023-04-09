import json
import os
import shutil
from typing import Any
# local
from mkdocs.config.defaults import MkDocsConfig
from .plugin_config import PlaceholderPluginConfig
from .generic.placeholder_data import Placeholder, InputType
from .style import generate_style_sheet
from .generic.validators import validator_to_dict


def _write_to_file(config: MkDocsConfig, relative_path: str, contents: str, open_mode: str) -> None:
    file_path = os.path.join(config.site_dir, relative_path)
    parent_dir = os.path.dirname(file_path)
    os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, open_mode) as f:
        f.write(contents)

def copy_assets_to_mkdocs_site_directory(config: MkDocsConfig, plugin_config: PlaceholderPluginConfig, placeholders: dict[str, Placeholder]):
    """
    Copy the JavaScript file to the site (if necessary) and replace the placeholder string with the actual data
    """
    # @TODO: merge everything into a single file if debug==false
    custom_js_path = os.path.join(config.site_dir, plugin_config.placeholder_js)
    if os.path.exists(custom_js_path):
        # use the file that is already in the site directory
        with open(custom_js_path, "r") as f:
            text = f.read()
    else:
        # use the default file supplied by the plugin
        input_file = get_resource_path("assets/placeholder-data.js")
        with open(input_file, "r") as f:
            text = f.read()

    if plugin_config.placeholder_css:
        theme_name = config.theme.name or "mkdocs"
        css_text = generate_style_sheet(theme_name, plugin_config.debug_javascript)
        _write_to_file(config, plugin_config.placeholder_css, css_text, "a")

    # Add extra JS
    if (plugin_config.placeholder_extra_js):
        with open(plugin_config.placeholder_extra_js, "r") as f:
            extra_js = f.read()

        text = "///// Custom extra JS code /////\n" + extra_js + "\n///// Normal JS code /////\n" + text

    # Generate placeholder data and inject them in the JavaScript file
    text = text.replace("__MKDOCS_PLACEHOLDER_PLUGIN_NEW_JSON__", generate_new_placeholder_json(placeholders, plugin_config))
    _write_to_file(config, plugin_config.placeholder_js, text, "w")

    parent_dir = os.path.dirname(custom_js_path)
    shutil.copy(get_resource_path("assets/placeholder.min.js"), parent_dir)
    shutil.copy(get_resource_path("assets/placeholder.min.js.map"), parent_dir)


def get_resource_path(name: str) -> str:
    """
    Gets the path to a file in the same directory as this file
    """
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, name)


def generate_new_placeholder_json(placeholders: dict[str, Placeholder], plugin_config: PlaceholderPluginConfig) -> str:
    """
    Generate the JSON string, that will replace the placeholder in the JavaScript file
    """
    placeholder_data_list = []
    validator_map = {}

    for placeholder in placeholders.values():
        placeholder_data = {
            "name": placeholder.name,
            "description": placeholder.description,
            "read_only": placeholder.read_only,
            "allow_inner_html": placeholder.replace_everywhere,
        }
        if placeholder.input_type == InputType.Checkbox:
            placeholder_data.update({
                "type": "checkbox",
                "value_checked": placeholder.values["checked"],
                "value_unchecked": placeholder.values["unchecked"],
                "checked_by_default": bool(placeholder.default_value == "checked"),
            })
        elif placeholder.input_type == InputType.Dropdown:
            # Figure out the index of the item selected by default
            default_index = 0
            for index, value in enumerate(placeholder.values.keys()):
                if placeholder.default_value == value:
                    default_index = index

            placeholder_data.update({
                "type": "dropdown",
                "default_index": default_index,
                "options": [{"display_name": key, "value": value} for key, value in placeholder.values.items()],
            })
        elif placeholder.input_type == InputType.Field:
            placeholder_data.update({
                "type": "textbox",
                "allow_recursive": True, # @TODO: read from config
                "validators": [v.id for v in placeholder.validator_list],
            })

            if placeholder.default_function:
                placeholder_data["default_function"] = placeholder.default_function
            else:
                placeholder_data["default_value"] = placeholder.default_value

        else:
            raise Exception(f"Unexpected input type: {placeholder.input_type}")

        placeholder_data_list.append(placeholder_data)

        for validator in placeholder.validator_list:
            # deduplicate validators
            validator_map[validator.id] = validator_to_dict(validator)

    result_object = {
        "placeholder_list": placeholder_data_list,
        "settings": {
            "debug": plugin_config.debug_javascript,
            "delay_millis": plugin_config.replace_delay_millis,
        },
        "validators": list(validator_map.values()),
    }
    return json.dumps(result_object, indent=None, sort_keys=False)

import json
import os
from typing import Any
# local
from mkdocs.config.defaults import MkDocsConfig
from .plugin_config import PlaceholderPluginConfig
from .placeholder_data import Placeholder, InputType
from .style import generate_style_sheet


def copy_assets_to_mkdocs_site_directory(config: MkDocsConfig, plugin_config: PlaceholderPluginConfig, placeholders: dict[str, Placeholder]):
    """
    Copy the JavaScript file to the site (if necessary) and replace the placeholder string with the actual data
    """
    custom_js_path = os.path.join(config.site_dir, plugin_config.placeholder_js)
    if os.path.exists(custom_js_path):
        # use the file that is already in the site directory
        with open(custom_js_path, "r") as f:
            text = f.read()
    else:
        # use the default file supplied by the plugin
        text = ""
        current_dir = os.path.dirname(__file__)
        js_dir = os.path.join(current_dir, "javascript")
        for file_name in sorted(os.listdir(js_dir)):
            with open(os.path.join(js_dir, file_name), "r") as f:
                text += f.read()
        # input_file = get_resource_path("../javascript/placeholder-plugin.js")
    
    # Generate placeholder data and inject them in the JavaScript file
    placeholder_data_json = generate_placeholder_json(config.theme.name, placeholders, plugin_config)
    text = text.replace("__MKDOCS_PLACEHOLDER_PLUGIN_JSON__", placeholder_data_json)

    # write back the results
    parent_dir = os.path.dirname(custom_js_path)
    os.makedirs(parent_dir, exist_ok=True)
    with open(custom_js_path, "w") as f:
        f.write(text)


def get_resource_path(name: str) -> str:
    """
    Gets the path to a file in the same directory as this file
    """
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, name)


def generate_placeholder_json(theme_name: str, placeholders: dict[str, Placeholder], plugin_config: PlaceholderPluginConfig) -> str:
    """
    Generate the JSON string, that will replace the placeholder in the JavaScript file
    """
    checkbox_data = {}
    dropdown_data = {}
    textbox_data = {}
    common_data = {}

    for placeholder in placeholders.values():
        if placeholder.input_type == InputType.Checkbox:
            checkbox_data[placeholder.name] = {
                "default_value": bool(placeholder.default_value == "checked"),
                "checked": placeholder.values["checked"],
                "unchecked": placeholder.values["unchecked"],
            }
        elif placeholder.input_type == InputType.Dropdown:
            # Figure out the index of the item selected by default
            default_index = 0
            for index, value in enumerate(placeholder.values.keys()):
                if placeholder.default_value == value:
                    default_index = index

            dropdown_data[placeholder.name] = {
                "default_index": default_index,
                "options": [[key, value] for key, value in placeholder.values.items()],
            }
        elif placeholder.input_type == InputType.Field:
            td: dict[str, Any] = {
                "value": placeholder.default_value,
            }
            vp = placeholder.validator_preset
            if vp:
                if vp.must_match_regex:
                    td["must_match"] = {
                        "regex": vp.must_match_regex,
                        "message": vp.must_match_message or f"Must match regular expression '{vp.must_match_regex}'"
                    }
                if vp.should_match_regex:
                    td["should_match"] = {
                        "regex": vp.should_match_regex,
                        "message": vp.should_match_message or f"Must match regular expression '{vp.should_match_regex}'"
                    }
            textbox_data[placeholder.name] = td
        else:
            raise Exception(f"Unexpected input type: {placeholder.input_type}")

        common_data[placeholder.name] = {
            "description": placeholder.description,
            "read_only": placeholder.read_only,
            "replace_everywhere": placeholder.replace_everywhere,
        }

    custom_css = generate_style_sheet(theme_name)

    result_object = {
        "checkbox": checkbox_data,
        "custom_css": custom_css,
        "dropdown": dropdown_data,
        "common": common_data,
        "textbox": textbox_data,
        "delay_millis": plugin_config.replace_delay_millis,
        "auto_table_apply_button": plugin_config.add_apply_table_column,
        "auto_table_hide_read_only": not plugin_config.table_default_show_readonly,
        "reload": plugin_config.reload_on_change,
        "debug": plugin_config.debug_javascript,
    }
    return json.dumps(result_object, indent=None, sort_keys=False)

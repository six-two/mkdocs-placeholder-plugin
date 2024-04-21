import logging
import os
# pip dependency
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from ..generic import set_logger

# local
from ..generic.config import PlaceholderConfig
from .style import generate_mkdocs_style_sheet
from .plugin_config import PlaceholderPluginConfig
from ..generic.config.configuration import parse_configuration_file
from ..assets import copy_assets_to_directory_debuggable, copy_assets_to_directory_combined, COMBINED_FILE_NAME, DEBUGGABLE_CODE_FILE_NAME, DEBUGGABLE_DATA_FILE_NAME
from ..generic import set_warnings_enabled

def initialize_plugin(mkdocs_config: MkDocsConfig, plugin_config: PlaceholderPluginConfig) -> PlaceholderConfig:
    # To get the correct looks, the logger needs to have the correct name
    logger = logging.getLogger("mkdocs.plugins.placeholder")
    set_logger(logger)

    placeholder_config = find_and_parse_configuration_file(mkdocs_config, plugin_config)
    set_warnings_enabled(placeholder_config.settings.show_warnings)

    register_asset_files(mkdocs_config, plugin_config, placeholder_config)

    return placeholder_config


def register_asset_files(mkdocs_config: MkDocsConfig, plugin_config: PlaceholderPluginConfig, placeholder_config: PlaceholderConfig) -> None:
    # Make sure that the custom JS is included on every page
    # Which output files are generated is determined by whether the debugging is enabled
    js_file_name_list = [DEBUGGABLE_CODE_FILE_NAME, DEBUGGABLE_DATA_FILE_NAME] if placeholder_config.settings.debug_javascript else [COMBINED_FILE_NAME]
    for file_name in js_file_name_list:
        js_file_path = os.path.join(plugin_config.js_output_dir, file_name)
        # The linter gives a warning here, but it should be fine:
        # Breaking change: config.extra_javascript is no longer a plain list of strings, but instead a list of ExtraScriptValue items. So you can no longer treat the list values as strings. If you want to keep compatibility with old versions, just always reference the items as str(item) instead. And you can still append plain strings to the list if you wish.
        # Source: https://www.mkdocs.org/about/release-notes/#version-150-2023-07-26
        # My note: If I upgraded to use the correct type, it would require MkDocs 1.5.0
        add_to_list_if_not_already_exists(mkdocs_config.extra_javascript, js_file_path) # type: ignore

    # Make sure that the custom CSS is included on every page
    if plugin_config.placeholder_css:
        add_to_list_if_not_already_exists(mkdocs_config.extra_css, plugin_config.placeholder_css)


def find_and_parse_configuration_file(mkdocs_config: MkDocsConfig, plugin_config: PlaceholderPluginConfig) -> PlaceholderConfig:
    if os.path.exists(plugin_config.placeholder_file):
        # Default to resolving paths relative to the current working directory
        return parse_configuration_file(plugin_config.placeholder_file)
    else:
        # If the above fails, look up relative to the configuration file. Useful if you do something like the following:
        # $ mkdocs gh-deploy --config-file ../my-project/mkdocs.yml --remote-branch master
        # Which is currently the recommended way to deploy with gitlab pages (as user page). SEE https://www.mkdocs.org/user-guide/deploying-your-docs/
        config_path = os.path.join(os.path.dirname(mkdocs_config.config_file_path), plugin_config.placeholder_file)
        if os.path.exists(config_path):
            return parse_configuration_file(config_path)
        else:
            raise PluginError(f"Could not resolve the file '{plugin_config.placeholder_file}' either relatively to the current working directory or to the configuration file")


def add_to_list_if_not_already_exists(the_list: list[str], value: str):
    if value not in the_list:
        the_list.append(value)


def _write_to_file(config: MkDocsConfig, relative_path: str, contents: str, open_mode: str) -> None:
    file_path = os.path.join(config.site_dir, relative_path)
    parent_dir = os.path.dirname(file_path)
    os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, open_mode) as f:
        f.write(contents)


def copy_assets_to_mkdocs_site_directory(mkdocs_config: MkDocsConfig, plugin_config: PlaceholderPluginConfig, placeholder_config: PlaceholderConfig):
    """
    Copy the JavaScript file to the site (if necessary) and replace the placeholder string with the actual data
    """
    if plugin_config.placeholder_css:
        theme_name = mkdocs_config.theme.name or "mkdocs"
        css_text = generate_mkdocs_style_sheet(theme_name, placeholder_config.settings.debug_javascript, placeholder_config.settings.inline_editor_icons)
        _write_to_file(mkdocs_config, plugin_config.placeholder_css, css_text, "a")

    # Add extra JS
    output_directory = os.path.join(mkdocs_config.site_dir, plugin_config.js_output_dir)
    extra_js = plugin_config.placeholder_extra_js if plugin_config.placeholder_extra_js else None

    if placeholder_config.settings.debug_javascript:
        copy_assets_to_directory_debuggable(placeholder_config, output_directory, extra_js)
    else:
        copy_assets_to_directory_combined(placeholder_config, output_directory, extra_js)


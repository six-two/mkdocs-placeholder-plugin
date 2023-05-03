import logging
import os
# pip dependency
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from ..generic import set_logger
from mkdocs.utils import warning_filter

# local files
# local
from ..generic.config import PlaceholderConfig
from .style import generate_mkdocs_style_sheet
from .plugin_config import PlaceholderPluginConfig
from ..generic.config.configuration import parse_configuration_file
from ..assets import copy_assets_to_directory_debuggable
from ..generic import set_warnings_enabled

def initialize_plugin(mkdocs_config: MkDocsConfig, plugin_config: PlaceholderPluginConfig) -> PlaceholderConfig:
    # To get the correct looks, the logger needs to have the correct name
    logger = logging.getLogger("mkdocs.plugins.placeholder")
    logger.addFilter(warning_filter)
    set_logger(logger)

    # Make sure that the custom JS is included on every page
    placeholder_js = os.path.join(plugin_config.js_output_dir, "placeholder.min.js")
    if placeholder_js not in mkdocs_config.extra_javascript:
        mkdocs_config.extra_javascript.append(placeholder_js)

    placeholder_js = os.path.join(plugin_config.js_output_dir, "placeholder-data.js")
    if placeholder_js not in mkdocs_config.extra_javascript:
        mkdocs_config.extra_javascript.append(placeholder_js)

    # Make sure that the custom CSS is included on every page
    if plugin_config.placeholder_css:
        if plugin_config.placeholder_css not in mkdocs_config.extra_css:
            mkdocs_config.extra_css.append(plugin_config.placeholder_css)

    # Immediatley parse the placeholder file, so that all following methods can use the information
    if os.path.exists(plugin_config.placeholder_file):
        # Default to resolving paths relative to the current working directory
        config_path = plugin_config.placeholder_file
    else:
        # If the above fails, look up relative to the configuration file. Useful if you do something like the following:
        # $ mkdocs gh-deploy --config-file ../my-project/mkdocs.yml --remote-branch master
        # Which is currently the recommended way to deploy with gitlab pages (as user page). SEE https://www.mkdocs.org/user-guide/deploying-your-docs/
        config_path = os.path.join(os.path.dirname(mkdocs_config.config_file_path), plugin_config.placeholder_file)
        if not os.path.exists(config_path):
            raise PluginError(f"Could not resolve the file '{plugin_config.placeholder_file}' either relatively to the current working directory or to the configuration file")

    placeholder_configuration = parse_configuration_file(config_path)
    set_warnings_enabled(placeholder_configuration.settings.show_warnings)

    return placeholder_configuration


def _write_to_file(config: MkDocsConfig, relative_path: str, contents: str, open_mode: str) -> None:
    file_path = os.path.join(config.site_dir, relative_path)
    parent_dir = os.path.dirname(file_path)
    os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, open_mode) as f:
        f.write(contents)


def copy_assets_to_mkdocs_site_directory(mkdocs_config: MkDocsConfig, plugin_config: PlaceholderPluginConfig, placeholder_configuration: PlaceholderConfig):
    """
    Copy the JavaScript file to the site (if necessary) and replace the placeholder string with the actual data
    """
    if plugin_config.placeholder_css:
        theme_name = mkdocs_config.theme.name or "mkdocs"
        css_text = generate_mkdocs_style_sheet(theme_name, placeholder_configuration.settings.debug_javascript)
        _write_to_file(mkdocs_config, plugin_config.placeholder_css, css_text, "a")

    # Add extra JS
    output_directory = os.path.join(mkdocs_config.site_dir, plugin_config.js_output_dir)
    extra_js = plugin_config.placeholder_extra_js if plugin_config.placeholder_extra_js else None

    # @TODO: merge everything into a single file if debug_js==false
    copy_assets_to_directory_debuggable(placeholder_configuration, output_directory, extra_js)


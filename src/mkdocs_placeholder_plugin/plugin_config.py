from mkdocs.config.config_options import Type
from mkdocs.config.base import Config

# Moved to an extra file to prevent cyclic dependency errors
class PlaceholderPluginConfig(Config):
    """
    The plugin config, that will be parsed from the settings supplied in `mkdocs.yaml`
    """
    # Can be used to disable the plugin
    enabled = Type(bool, default=True)
    # Show warnings if potential errors are found
    show_warnings = Type(bool, default=True)
    # Reload the page when a significant change (pressed Enter in textbox, change in checkbox or dropdown)
    reload_on_change = Type(bool, default=True)
    # Add the "Apply the new values by clicking on this text" to placeholder input tables
    add_apply_table_column = Type(bool, default=False)
    # files to perform static replacements for:
    static_pages = Type(list, default=[])
    # The file where you define the placeholders
    placeholder_file = Type(str, default="placeholder-plugin.yaml")
    # Output loaction for the custom JS file
    placeholder_js = Type(str, default="assets/javascripts/placeholder-plugin.js")
    # Replace delay millis
    replace_delay_millis = Type(int, default=0)
    # Default values for place4holder input tables
    table_default_show_readonly = Type(bool, default=False)
    table_default_type = Type(str, default="simple")
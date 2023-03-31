from mkdocs.config.config_options import Type
from mkdocs.config.base import Config

# Moved to an extra file to prevent cyclic dependency errors
class PlaceholderPluginConfig(Config):
    """
    The plugin config, that will be parsed from the settings supplied in `mkdocs.yaml`
    """
    # Can be used to disable the plugin
    enabled = Type(bool, default=True)
    # Automatically add input tables to the top of each page with placeholders
    auto_placeholder_tables = Type(bool, default=False)
    # Use collapsible admonitions
    auto_placeholder_tables_collapsible = Type(bool, default=True)
    # Create placeholder tables dynamically (with JavaScript), instead of at build time
    auto_placeholder_tables_javascript = Type(bool, default=False)
    # Enable logging of debuggin information to the browser's console
    debug_javascript = Type(bool, default=False)
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
    # Output loaction for the custom JS file. This overwrites the javascript code provided by the plugin
    placeholder_js = Type(str, default="assets/javascripts/placeholder-plugin.js")
    # Provide additional javascript for example for hooks, providing functions, etc
    placeholder_extra_js = Type(str, default="")
    # Replace delay millis
    replace_delay_millis = Type(int, default=0)
    # CSS file. If it exists, the contents will be appended to. add empty string to not include the default styles
    placeholder_css = Type(str, default="assets/javascripts/placeholder-plugin.css")
    # Default values for place4holder input tables
    table_default_show_readonly = Type(bool, default=False)
    table_default_type = Type(str, default="simple")

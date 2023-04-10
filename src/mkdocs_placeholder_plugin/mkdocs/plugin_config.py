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
    # The file where you define the placeholders
    placeholder_file = Type(str, default="placeholder-plugin.yaml")
    # Output loaction for the custom JS file. This overwrites the javascript code provided by the plugin
    js_output_dir = Type(str, default="assets/javascripts/")
    # Provide additional javascript for example for hooks, providing functions, etc
    placeholder_extra_js = Type(str, default="")
    # CSS file. If it exists, the contents will be appended to. add empty string to not include the default styles
    placeholder_css = Type(str, default="assets/javascripts/placeholder-plugin.css")
    # Default values for place4holder input tables
    table_default_type = Type(str, default="simple")

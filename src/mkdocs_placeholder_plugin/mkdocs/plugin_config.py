from mkdocs.config.config_options import Type
from mkdocs.config.base import Config

# Moved to an extra file to prevent cyclic dependency errors
class PlaceholderPluginConfig(Config):
    """
    The plugin config, that will be parsed from the settings supplied in `mkdocs.yaml`
    """
    # Can be used to disable the plugin
    enabled = Type(bool, default=True)
    # Output loaction for the custom JS file. This overwrites the javascript code provided by the plugin
    js_output_dir = Type(str, default="assets/javascripts/")
    # CSS file. If it exists, the contents will be appended to. add empty string to not include the default styles
    placeholder_css = Type(str, default="assets/javascripts/placeholder-plugin.css")
    # Provide additional javascript for example for hooks, providing functions, etc
    placeholder_extra_js = Type(str, default="")
    # The file where you define the placeholders
    placeholder_file = Type(str, default="placeholder-plugin.yaml")

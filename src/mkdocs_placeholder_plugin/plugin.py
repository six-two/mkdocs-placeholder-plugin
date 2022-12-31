from functools import wraps
import os
import traceback
from typing import Callable
# pip dependency
import mkdocs
from mkdocs.config.config_options import Type
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.config.base import Config

# local files
from .assets import PLACEHOLDER_JS, copy_asset_if_target_file_does_not_exist, replace_text_in_file
from .utils import load_placeholder_data, generate_placeholder_json, search_for_invalid_variable_names_in_input_field_targets
from .static_replacer import StaticReplacer
from .input_table import InputTableGenerator
from . import set_warnings_enabled, debug

DEFAULT_JS_PATH = "assets/javascripts/placeholder-plugin.js"

def convert_exceptions(function: Callable) -> Callable:
    @wraps(function)
    def wrap(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as ex:
            debug(f"Fatal exception occurred, stack trace:\n{traceback.format_exc()}")
            if isinstance(ex, mkdocs.exceptions.PluginError):
                raise mkdocs.exceptions.PluginError(f"[placeholder] {ex}")
            else:
                # Add the information, that it is a normal uncaught excaption
                raise mkdocs.exceptions.PluginError(f"[placeholder] Uncaught exception: {ex}")
    return wrap


class PlaceholderPluginConfig(Config):
    # Can be used to disable the plugin
    enabled = Type(bool, default=True)
    # Show warnings if potential errors are found
    show_warnings = Type(bool, default=True)
    # Add the "Apply the new values by clicking on this text" to placeholder input tables
    add_apply_table_column = Type(bool, default=False)
    # files to perform static replacements for:
    static_pages = Type(list, default=[])
    # The file where you define the placeholders
    placeholder_file = Type(str, default="placeholder-plugin.yaml")
    # Output loaction for the custom JS file
    placeholder_js = Type(str, default=DEFAULT_JS_PATH)
    # Replace delay millis
    replace_delay_millis = Type(int, default=0)
    # Default values for place4holder input tables
    table_default_show_readonly = Type(bool, default=False)
    table_default_type = Type(str, default="simple")


class PlaceholderPlugin(BasePlugin[PlaceholderPluginConfig]):
    @convert_exceptions
    def on_config(self, config: MkDocsConfig, **kwargs) -> Config:
        """
        Called once when the config is loaded.
        It will make modify the config and initialize this plugin.
        """
        if self.config.enabled:
            self.initialize_plugin(config)

        return config

    def on_page_markdown(self, markdown: str, page, config: MkDocsConfig, files) -> str:
        """
        The page_markdown event is called after the page's markdown is loaded from file and can be used to alter the Markdown source text. The metadata has been stripped off and is available as page.meta at this point.
        See: https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown
        """
        if self.config.enabled:
            return self.table_generator.handle_markdown(markdown)
        else:
            return markdown

    @convert_exceptions
    def on_post_build(self, config: MkDocsConfig) -> None:
        """
        Copy the default files if the user hasn't supplied his/her own version
        """
        if self.config.enabled:
            self.after_build_action(config)

    def initialize_plugin(self, config: MkDocsConfig) -> None:
        set_warnings_enabled(self.config.show_warnings)

        # Make sure that the custom JS is included on every page
        custom_js_path = self.config.placeholder_js
        extra_js = config.extra_javascript
        if custom_js_path not in extra_js:
            extra_js.append(custom_js_path)

        # Immediatley parse the placeholder file, so that all following methods can use the information
        placeholder_file = self.config.placeholder_file
        self.placeholders = load_placeholder_data(placeholder_file)

        default_show_readonly = self.config.table_default_show_readonly
        default_table_type = self.config.table_default_type
        add_apply_table_column = self.config.add_apply_table_column
        self.table_generator = InputTableGenerator(self.placeholders, default_show_readonly, default_table_type, add_apply_table_column)

    def after_build_action(self, config: MkDocsConfig) -> None:
        # copy over template
        output_dir = config.site_dir
        custom_js_path = self.config.placeholder_js
        copy_asset_if_target_file_does_not_exist(output_dir, custom_js_path, PLACEHOLDER_JS)
        
        # replace placeholder in template with the actual data JSON
        full_custom_js_path = os.path.join(output_dir, custom_js_path)
        placeholder_data_json = generate_placeholder_json(self.placeholders)
        replace_text_in_file(full_custom_js_path, {
            "__MKDOCS_PLACEHOLDER_PLUGIN_JSON__": placeholder_data_json,
            "__MKDOCS_REPLACE_TRIGGER_DELAY_MILLIS__": str(self.config.replace_delay_millis),
        })

        # Check the variable names linked to input fields
        valid_variable_names = list(self.placeholders.keys())
        search_for_invalid_variable_names_in_input_field_targets(output_dir, valid_variable_names)

        # Replace placeholders in files marked for static replacements
        replacement_list = self.config.static_pages
        if replacement_list:
            static_replacer = StaticReplacer(self.placeholders, replacement_list)
            static_replacer.process_output_folder(output_dir)


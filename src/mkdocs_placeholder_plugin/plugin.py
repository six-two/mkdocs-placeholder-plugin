from functools import wraps
import traceback
from typing import Callable
# pip dependency
import mkdocs
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.config.base import Config

# local files
from .plugin_config import PlaceholderPluginConfig
from .placeholder_data import load_placeholder_data, search_for_invalid_variable_names_in_input_field_targets
from .assets import copy_assets_to_mkdocs_site_directory
from .static_replacer import StaticReplacer
from .input_table import InputTableGenerator
from . import set_warnings_enabled, debug


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

    @convert_exceptions
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

        # Instanciate a table generator
        self.table_generator = InputTableGenerator(self.placeholders,
            self.config.table_default_show_readonly,
            self.config.table_default_type,
            self.config.add_apply_table_column)

    def after_build_action(self, config: MkDocsConfig) -> None:
        copy_assets_to_mkdocs_site_directory(config.site_dir, self.config, self.placeholders)

        # Check the variable names linked to input fields
        valid_variable_names = list(self.placeholders.keys())
        search_for_invalid_variable_names_in_input_field_targets(config.site_dir, valid_variable_names)

        # Replace placeholders in files marked for static replacements
        replacement_list = self.config.static_pages
        if replacement_list:
            static_replacer = StaticReplacer(self.placeholders, replacement_list)
            static_replacer.process_output_folder(config.site_dir)


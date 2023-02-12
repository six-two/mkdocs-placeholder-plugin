from functools import wraps
import traceback
from typing import Callable
# pip dependency
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.config.base import Config
from mkdocs.exceptions import PluginError

# local files
from .plugin_config import PlaceholderPluginConfig
from .placeholder_data import load_placeholder_data
from .assets import copy_assets_to_mkdocs_site_directory
from .static_replacer import StaticReplacer
from .input_tag_handler import create_normal_input_class_handler
from .auto_input_table import AutoTableInserter
from .input_table import InputTableGenerator
from . import set_warnings_enabled, debug


def convert_exceptions(function: Callable) -> Callable:
    @wraps(function)
    def wrap(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as ex:
            debug(f"Fatal exception occurred, stack trace:\n{traceback.format_exc()}")
            if isinstance(ex, PluginError):
                raise PluginError(f"[placeholder] {ex}")
            else:
                # Add the information, that it is a normal uncaught excaption
                raise PluginError(f"[placeholder] Uncaught exception: {ex}")
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
            if self.config.auto_placeholder_tables:
                markdown = self.auto_table_inserter.add_to_page(markdown)
            return self.table_generator.handle_markdown(markdown)
        else:
            return markdown

    @convert_exceptions
    def on_page_content(self, html: str, page, config: MkDocsConfig, files) -> str:
        """
        The page_content event is called after the Markdown text is rendered to HTML (but before being passed to a template) and can be used to alter the HTML body of the page.
        """
        if self.config.enabled:
            file_path = page.file.src_path
            return self.input_tag_modifier.process_string(file_path, html)
        else:
            return html


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

        # Set the value for inputs to inform the user to enable JavaScript
        # Line numbers in output are disabled, since we need to call this after the markdown was parsed.
        # Otherwise stuff in listings and co may be unintentianally modified/checked
        self.input_tag_modifier = create_normal_input_class_handler(self.placeholders, add_line_in_warning=False)

        if self.config.auto_placeholder_tables:
            self.auto_table_inserter = AutoTableInserter(self.placeholders, self.config)
            if self.config.auto_placeholder_tables_collapsible:
                ensure_extensions_loaded(config, ["admonition", "pymdownx.details"])

    def after_build_action(self, config: MkDocsConfig) -> None:
        copy_assets_to_mkdocs_site_directory(config, self.config, self.placeholders)

        # Replace placeholders in files marked for static replacements
        replacement_list = self.config.static_pages
        if replacement_list:
            static_replacer = StaticReplacer(self.placeholders, replacement_list)
            static_replacer.process_output_folder(config.site_dir)


def ensure_extensions_loaded(config: MkDocsConfig, extensions: list[str]) -> None:
    for extension in extensions:
        if extension not in config.markdown_extensions:
            config.markdown_extensions.append(extension)

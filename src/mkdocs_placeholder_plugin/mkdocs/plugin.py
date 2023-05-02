from functools import wraps
import os
import traceback
from typing import Callable
# pip dependency
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.config.base import Config
from mkdocs.exceptions import PluginError

# local files
# local
from ..generic.config import PlaceholderConfig
from .style import generate_mkdocs_style_sheet
from .plugin_config import PlaceholderPluginConfig
from ..generic.config.configuration import parse_configuration_file
from ..assets import copy_assets_to_directory_debuggable
from ..generic.static_replacer import StaticReplacer
from ..generic.input_tag_handler import create_normal_input_class_handler
from ..generic.auto_input_table import AutoTableInserter
from ..generic.input_table import InputTableGenerator
from ..generic import set_warnings_enabled, warning, PlaceholderConfigError, PlaceholderPageError
from ..generic.placeholder_replacer import DynamicPlaceholderPreprocessor


def convert_exceptions(function: Callable) -> Callable:
    @wraps(function)
    def wrap(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as ex:
            warning(f"Fatal exception occurred, stack trace:\n{traceback.format_exc()}")
            if isinstance(ex, PluginError):
                raise PluginError(f"[placeholder] {ex}")
            elif isinstance(ex, PlaceholderConfigError) or isinstance(ex, PlaceholderPageError):
                raise PluginError(str(ex))
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
            if True: #@TODO
                markdown = self.dynamic_placeholder_preprocessor.handle_markdown_page(markdown)
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
            if True: #@TODO
                html = self.dynamic_placeholder_preprocessor.handle_html_page(html)

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
        # Make sure that the custom JS is included on every page
        placeholder_js = os.path.join(self.config.js_output_dir, "placeholder.min.js")
        if placeholder_js not in config.extra_javascript:
            config.extra_javascript.append(placeholder_js)

        placeholder_js = os.path.join(self.config.js_output_dir, "placeholder-data.js")
        if placeholder_js not in config.extra_javascript:
            config.extra_javascript.append(placeholder_js)

        # Make sure that the custom CSS is included on every page
        if self.config.placeholder_css:
            if self.config.placeholder_css not in config.extra_css:
                config.extra_css.append(self.config.placeholder_css)

        # Immediatley parse the placeholder file, so that all following methods can use the information
        if os.path.exists(self.config.placeholder_file):
            # Default to resolving paths relative to the current working directory
            config_path = self.config.placeholder_file
        else:
            # If the above fails, look up relative to the configuration file. Useful if you do something like the following:
            # $ mkdocs gh-deploy --config-file ../my-project/mkdocs.yml --remote-branch master
            # Which is currently the recommended way to deploy with gitlab pages (as user page). SEE https://www.mkdocs.org/user-guide/deploying-your-docs/
            config_path = os.path.join(os.path.dirname(config.config_file_path), self.config.placeholder_file)
            if not os.path.exists(config_path):
                raise PluginError(f"Could not resolve the file '{self.config.placeholder_file}' either relatively to the current working directory or to the configuration file")

        self.configuration = parse_configuration_file(config_path)
        self.placeholders = self.configuration.placeholders
        set_warnings_enabled(self.configuration.settings.show_warnings)

        # Instanciate a table generator
        self.table_generator = InputTableGenerator(self.placeholders,
            False,
            self.config.table_default_type,
            False)

        self.dynamic_placeholder_preprocessor = DynamicPlaceholderPreprocessor(self.configuration)

        # Set the value for inputs to inform the user to enable JavaScript
        # Line numbers in output are disabled, since we need to call this after the markdown was parsed.
        # Otherwise stuff in listings and co may be unintentianally modified/checked
        self.input_tag_modifier = create_normal_input_class_handler(self.placeholders, add_line_in_warning=False)

        if self.config.auto_placeholder_tables:
            self.auto_table_inserter = AutoTableInserter(self.placeholders, self.config)
            if self.config.auto_placeholder_tables_collapsible:
                ensure_extensions_loaded(config, ["admonition", "pymdownx.details"])

    def after_build_action(self, config: MkDocsConfig) -> None:
        copy_assets_to_mkdocs_site_directory(config, self.config, self.configuration)

        # # Replace placeholders in files marked for static replacements
        # replacement_list = self.config.static_pages
        # if replacement_list:
        #     static_replacer = StaticReplacer(self.placeholders, replacement_list)
        #     static_replacer.process_output_folder(config.site_dir)


def ensure_extensions_loaded(config: MkDocsConfig, extensions: list[str]) -> None:
    for extension in extensions:
        if extension not in config.markdown_extensions:
            config.markdown_extensions.append(extension)


def _write_to_file(config: MkDocsConfig, relative_path: str, contents: str, open_mode: str) -> None:
    file_path = os.path.join(config.site_dir, relative_path)
    parent_dir = os.path.dirname(file_path)
    os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, open_mode) as f:
        f.write(contents)


def copy_assets_to_mkdocs_site_directory(config: MkDocsConfig, plugin_config: PlaceholderPluginConfig, generic_config: PlaceholderConfig):
    """
    Copy the JavaScript file to the site (if necessary) and replace the placeholder string with the actual data
    """
    if plugin_config.placeholder_css:
        theme_name = config.theme.name or "mkdocs"
        css_text = generate_mkdocs_style_sheet(theme_name, generic_config.settings.debug_javascript)
        _write_to_file(config, plugin_config.placeholder_css, css_text, "a")

    # Add extra JS
    output_directory = os.path.join(config.site_dir, plugin_config.js_output_dir)
    extra_js = plugin_config.placeholder_extra_js if plugin_config.placeholder_extra_js else None

    # @TODO: merge everything into a single file if debug_js==false
    copy_assets_to_directory_debuggable(generic_config, output_directory, extra_js)


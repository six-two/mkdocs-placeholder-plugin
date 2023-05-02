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
from ..generic import set_warnings_enabled, warning, PlaceholderConfigError, PlaceholderPageError
from ..generic.page_processor import PageProcessor


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
            markdown = self.page_processor.process_page_markdown(markdown)

        return markdown

    @convert_exceptions
    def on_page_content(self, html: str, page, config: MkDocsConfig, files) -> str:
        """
        The page_content event is called after the Markdown text is rendered to HTML (but before being passed to a template) and can be used to alter the HTML body of the page.
        """
        if self.config.enabled:
            html = self.page_processor.process_page_html(page.file.src_path, html)

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
        set_warnings_enabled(self.configuration.settings.show_warnings)

        self.page_processor = PageProcessor(self.configuration)


    def after_build_action(self, config: MkDocsConfig) -> None:
        copy_assets_to_mkdocs_site_directory(config, self.config, self.configuration)


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


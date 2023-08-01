from functools import wraps
import traceback
from typing import Callable
# pip dependency
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.exceptions import PluginError
# local files
from .plugin_config import PlaceholderPluginConfig
from ..generic import warning, PlaceholderConfigError, PlaceholderPageError
from ..generic.page_processor import PageProcessor
from .utils import initialize_plugin, copy_assets_to_mkdocs_site_directory


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
    def on_config(self, config: MkDocsConfig, **kwargs) -> MkDocsConfig:
        """
        Called once when the config is loaded.
        It will make modify the config and initialize this plugin.
        """
        if self.config.enabled:
            self.configuration = initialize_plugin(config, self.config)
            self.page_processor = PageProcessor(self.configuration)

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
            copy_assets_to_mkdocs_site_directory(config, self.config, self.configuration)


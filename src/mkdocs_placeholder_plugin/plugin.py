import os
# pip dependency
import mkdocs
from mkdocs.config.config_options import Type
from mkdocs.plugins import BasePlugin
from mkdocs.config.base import Config
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files
# local files
from . import warning


class PlaceholderPlugin(BasePlugin):
    config_scheme = (
        ("enable_dynamic", Type(bool, default=True)),
        ("static_pages", Type(list, default=[])),
        ("placeholder_file", Type(str, default="placeholder-plugin.yaml")),
    )

    def on_config(self, config: Config, **kwargs) -> Config:
        """
        Called once when the config is loaded.
        It will make modify the config and initialize this plugin.
        """
        # Make sure that the CSS and JS badge files are included on every page
        # badge_css_path = self.config["badge_css"] or DEFAULT_BADGE_CSS_PATH
        # extra_css = config["extra_css"]
        # if badge_css_path not in extra_css:
        #     extra_css.append(badge_css_path)

        # badge_js_path = self.config["badge_js"] or DEFAULT_BADGE_JS_PATH
        # extra_js = config["extra_javascript"]
        # if badge_js_path not in extra_js:
        #     extra_js.append(badge_js_path)

        # # Load the install badge data from the data file
        # current_dir = os.path.dirname(__file__)
        # install_badge_data_path = self.config["install_badge_data"] or INSTALL_BADGE_DATA
        # self.install_badge_manager = InstallBadgeManager(install_badge_data_path)

        warning("TODO")
        return config

    def on_page_markdown(self, markdown: str, page: Page, config: Config, files: Files) -> str:
        """
        The page_markdown event is called after the page's markdown is loaded from file and can be used to alter the Markdown source text. The meta- data has been stripped off and is available as page.meta at this point.
        See: https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown
        """
        warning("TODO")
        return markdown


    def on_post_build(self, config: Config) -> None:
        """
        Copy the default files if the user hasn't supplied his/her own version
        """
        # output_dir = config["site_dir"]
        # badge_css_path = self.config["badge_css"] or DEFAULT_BADGE_CSS_PATH
        # copy_asset_if_target_file_does_not_exist(output_dir, badge_css_path, BADGE_CSS)

        # badge_js_path = self.config["badge_js"] or DEFAULT_BADGE_JS_PATH
        # copy_asset_if_target_file_does_not_exist(output_dir, badge_js_path, BADGE_JS)
        warning("TODO")


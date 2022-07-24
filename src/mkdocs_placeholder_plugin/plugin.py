import json
import os
# pip dependency
import mkdocs
from mkdocs.config.config_options import Type
from mkdocs.plugins import BasePlugin
from mkdocs.config.base import Config
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files
import yaml # this should be included as an dependency of mkdocs: pip show mkdocs | grep -i yaml
# local files
from . import warning
from .assets import PLACEHOLDER_JS, copy_asset_if_target_file_does_not_exist, replace_text_in_file


DEFAULT_JS_PATH = "assets/javascripts/placeholder-plugin.js"

class PlaceholderPlugin(BasePlugin):
    config_scheme = (
        ("enable_dynamic", Type(bool, default=True)),
        ("static_pages", Type(list, default=[])),
        ("placeholder_file", Type(str, default="placeholder-plugin.yaml")),
        # Output loaction for the custom JS file
        ("placeholder_js", Type(str, default=DEFAULT_JS_PATH)),

    )

    def on_config(self, config: Config, **kwargs) -> Config:
        """
        Called once when the config is loaded.
        It will make modify the config and initialize this plugin.
        """
        # Make sure that the custom JS is included on every page
        custom_js_path = self.config["placeholder_js"]
        extra_js = config["extra_javascript"]
        if custom_js_path not in extra_js:
            extra_js.append(custom_js_path)

        # # Load the install badge data from the data file
        # current_dir = os.path.dirname(__file__)
        # install_badge_data_path = self.config["install_badge_data"] or INSTALL_BADGE_DATA
        # self.install_badge_manager = InstallBadgeManager(install_badge_data_path)

        return config

    # def on_page_markdown(self, markdown: str, page: Page, config: Config, files: Files) -> str:
    #     """
    #     The page_markdown event is called after the page's markdown is loaded from file and can be used to alter the Markdown source text. The meta- data has been stripped off and is available as page.meta at this point.
    #     See: https://www.mkdocs.org/dev-guide/plugins/#on_page_markdown
    #     """
    #     warning("TODO")
    #     return markdown


    def on_post_build(self, config: Config) -> None:
        """
        Copy the default files if the user hasn't supplied his/her own version
        """
        placeholder_file = self.config["placeholder_file"]
        if not os.path.exists(placeholder_file):
            raise mkdocs.exceptions.PluginError(f"Placeholder data file '{placeholder_file}' does not exist")
        try:
            # copy over template
            output_dir = config["site_dir"]
            custom_js_path = self.config["placeholder_js"]
            copy_asset_if_target_file_does_not_exist(output_dir, custom_js_path, PLACEHOLDER_JS)

            # load data
            with open(placeholder_file, "rb") as f:
                placeholder_data = yaml.safe_load(f)
            placeholder_data_json = json.dumps(placeholder_data, indent=None, sort_keys=False)
            
            # replace placeholder in template with the actual data JSON
            full_custom_js_path = os.path.join(output_dir, custom_js_path)
            replace_text_in_file(full_custom_js_path, "__MKDOCS_PLACEHOLDER_PLUGIN_JSON__", placeholder_data_json)
        except Exception as error:
            raise mkdocs.exceptions.PluginError(str(error))



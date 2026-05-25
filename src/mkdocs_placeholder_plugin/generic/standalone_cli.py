# @TODO: addapt this script to allow standalone badge replacement
import argparse
import os
import traceback
from typing import NamedTuple
import logging
import os
# pip dependency
from ..generic import set_logger

# local
from ..generic.config.configuration import parse_configuration_file
from ..assets import copy_assets_to_directory_debuggable, copy_assets_to_directory_combined, COMBINED_FILE_NAME, DEBUGGABLE_CODE_FILE_NAME, DEBUGGABLE_DATA_FILE_NAME
from ..generic import set_warnings_enabled
from ..generic.page_processor import PageProcessor
from ..generic.generic_style import generate_generic_style_sheet
from ..assets import copy_assets_to_directory_debuggable, copy_assets_to_directory_combined, COMBINED_FILE_NAME, DEBUGGABLE_CODE_FILE_NAME, DEBUGGABLE_DATA_FILE_NAME


DEFAULT_BADGE_CSS_PATH = "assets/stylesheets/placeholders.css"
DEFAULT_JS_PATH = "assets/javascripts/"


def exit_with_message(msg):
    print(msg)
    exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["markdown", "html", "both"], help="what phases to run. Run 'markdown' on the original markdown files and 'html' after you ran the site generator.")
    ap.add_argument("--docs", "-d", default=".", help="directory containing your markdown (or HTML) files (default: '.')")
    ap.add_argument("--placeholder-config", "-p", default="placeholder-plugin.yaml", help="placeholder YAML config file (default: placeholder-plugin.yaml)")
    ap.add_argument("--placeholder-extra-js", help="file with extra javascript functions, hooks, etc")
    # ap.add_argument("--theme", "-t", default="mkdocs", help="mkdocs theme to generate CSS for. You probably should not need this (default: mkdocs)")
    # Settings
    ap.add_argument("--file-encoding", "-E", default="utf-8", help="file encoding to read and write the markdown files (default: 'utf-8')")
    ap.add_argument("--css-path", default=DEFAULT_BADGE_CSS_PATH, help=f"the path where the CSS file will be written to if --copy-resources is used (default: {DEFAULT_BADGE_CSS_PATH})")
    ap.add_argument("--js-dir", default=DEFAULT_JS_PATH, help=f"the directory where the Javascript file will be written to if --copy-resources is used (default: {DEFAULT_JS_PATH})")

    args = ap.parse_args()

    logger = logging.getLogger("mkdocs.plugins.placeholder")
    set_logger(logger)

    placeholder_config = parse_configuration_file(args.placeholder_config)
    page_processor = PageProcessor(placeholder_config)
    set_warnings_enabled(placeholder_config.settings.show_warnings)

    # register_asset_files(mkdocs_config, plugin_config, placeholder_config)

    docs_dir = args.docs
    for dirpath, dir_names, file_names in os.walk(docs_dir):
        for file_name in file_names:
            if file_name.lower().split(".")[-1] in ["md", "html", "htm"]:
                file_path = os.path.join(dirpath, file_name)
                try:
                    with open(file_path, encoding=args.file_encoding) as f:
                        og_markdown = markdown = f.read()

                    if args.phase in ["markdown", "both"]:
                        markdown = page_processor.process_page_markdown(markdown)
                    # @TODO: investigate why I need the HTML and if I can do it during the markdown phase too? Otherwise needs call before and after the site generator is called
                    if args.phase in ["html", "both"]:
                        markdown = page_processor.process_page_html(file_path, markdown)

                    if markdown != og_markdown:
                        print(f"Modified: {file_path}")
                        with open(file_path, "w", encoding=args.file_encoding) as f:
                            f.write(markdown)
                except UnicodeDecodeError as ex:
                    print(f"Error reading file '{file_path}' with encoding '{args.file_encoding}'. Please make sure to specify the correct encoding with the --encoding flag.")
                    print("Original error:", ex)
                except Exception:
                    print(f"Error processing '{file_path}'")
                    traceback.print_exc()

    if args.phase in ["html", "both"]:
        copy_assets(args, placeholder_config)


def copy_assets(args, placeholder_config):
    if args.css_path:
        css_text = generate_generic_style_sheet(placeholder_config.settings.debug_javascript)
        _write_to_file(args.docs, args.css_path, css_text, "a")
        print(f"\nRemember to add '{args.css_path}' as extra_css")

    # Add extra JS
    # Which output files are generated is determined by whether the debugging is enabled
    output_directory = os.path.join(args.docs, args.js_dir)
    if placeholder_config.settings.debug_javascript:
        copy_assets_to_directory_debuggable(placeholder_config, output_directory, args.placeholder_extra_js)
        print(f"Also add '{os.path.join(args.js_dir, DEBUGGABLE_CODE_FILE_NAME)}' and '{os.path.join(args.js_path, DEBUGGABLE_DATA_FILE_NAME)}' as extra_javascript")
    else:
        copy_assets_to_directory_combined(placeholder_config, output_directory, args.placeholder_extra_js)
        print(f"Also add '{os.path.join(args.js_dir, COMBINED_FILE_NAME)}' as extra_javascript")


def _write_to_file(docs_dir: str, relative_path: str, contents: str, open_mode: str) -> None:
    file_path = os.path.join(docs_dir, relative_path)
    parent_dir = os.path.dirname(file_path)
    os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, open_mode) as f:
        f.write(contents)

#!/usr/bin/env python3
import argparse
# local files
from mkdocs_placeholder_plugin.utils import load_placeholder_data
from mkdocs_placeholder_plugin.static_replacer import StaticReplacer


def main() -> None:
    ap = argparse.ArgumentParser(description="Replaces placeholders in the specified files with their default values. This operation is inplace, so make sure the input files are backed up (or can be easily regenerated). This script does what the plugin can already do, but you can use it any time (and even without mkdocs).")
    ap.add_argument("-p", "--placeholder-file", required=True, help="the file containing the placeholder definitions (usually called placeholder-plugin.yaml)")
    ap.add_argument("-b", "--base-dir", default=".", help="the base dir used for the globs. This should probably be you mkdocs output dir. Defaults to the currect working directory")
    ap.add_argument("file_globs", nargs="+", help="a list of globs matching the files where the placeholders should be replcaed")
    args = ap.parse_args()

    replace_placeholders_in_files(args.placeholder_file, args.base_dir, args.file_globs)


def replace_placeholders_in_files(placeholder_data_file: str, base_dir: str, file_globs: list[str]) -> None:
    placeholders = load_placeholder_data(placeholder_data_file)
    static_replacer = StaticReplacer(placeholders, file_globs)
    static_replacer.process_output_folder(base_dir)


if __name__ == "__main__":
    main()

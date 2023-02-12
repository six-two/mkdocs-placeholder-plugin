# MkDocs Placeholder Plugin

[![PyPI version](https://img.shields.io/pypi/v/mkdocs-placeholder-plugin)](https://pypi.org/project/mkdocs-placeholder-plugin/)
![License](https://img.shields.io/pypi/l/mkdocs-placeholder-plugin)
![Python versions](https://img.shields.io/pypi/pyversions/mkdocs-placeholder-plugin)

This plugin allows you to have placeholders in your site, that can be dynamically replaced at runtime using JavaScript (see [demo page](https://mkdocs-placeholder-plugin.six-two.dev/demo/)).


## Documentation

This README is just a short intro to the package.
For a quick start and detailed information please see the [documentation](https://mkdocs-placeholder-plugin.six-two.dev/).
The documentation is also available in the `docs` folder of the source code and can be built localy with [MkDocs](https://www.mkdocs.org/).


## Notable changes

### HEAD

- Split JavaScript code into multiple files and made it available via the global `PlaceholderData` and `PlaceholderPlugin` objects.
    These interfaces are not stable, so you should probably not try to rely on them to much.
- Added `replace_everywhere` attribute for placeholders
- Changes to textbox values are only stored, when you press `Enter`
- Dynamically generated tables now honor `add_apply_table_column`
- Improved JavaScript debugging: timestamps, more messages, and you can disable the page reload
- Some visual fixes, mainly for the `Material for MkDocs` theme

### Version 0.2.2

- Improved placeholder input tables:
    - Can now specify which columns to use (and their order)
    - Only show apply values column, if at least one column contains input elements
- Properly handle checkboxes and dropdown menus when performing static replacements
- Hide JavaScript console output by default
- Generate automatic placeholder table dynamically, since if checkboxes / dropdowns are used, it can not be predicted, which values are used on the page.
- Added `description-or-name` column type to placeholder tables.

### Version 0.2.1

- Add option to reload the page if a checkbox/dropdown is changed or a text field is changed and `Enter` is pressed (to immediately show the new values).
    This is enabled by default.
- Set initial value for placeholder input fields to "Please enable JavaScript"
- Added option to automatically insert placeholder input tables at the top of each page

### Version 0.2.0

- Added new input types (checkbox & dropdown menu)
- Also allow numbers in placeholder names (everywhere except the first character)
- Moved to typed mkdocs config (now requires mkdocs 1.4+)
- Disable input elements for read only placeholders
- Moved a lot of code around, significantly changed JavaScript file

### Version 0.1.3

- Placeholder config: Placeholders can now have attributes (like `description`)
- Tables with inputs for all placeholders on a page can now be generated via `<placeholdertable>` elements
- Stack traces for fatal exceptions can now be seen with the `-v` flag (`mkdocs serve -v`)
- When performing static replacements, the contents are now HTML escaped
- Added script `mkdocs-placeholder-replace-static.py`

### Version 0.1.2

- Implemented static replacements for user-selected pages
- Added timing options. This should  make it possible to use with MermaidJS diagrams, but may not always work

### Version 0.1.1

- Show a warning if an `input` element references a non-existent variable
- Show a warning if a variable name does not match the recommended format
- Perform type checks/conversions when loading placeholder data from the data file

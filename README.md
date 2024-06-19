# MkDocs Placeholder Plugin

[![PyPI version](https://img.shields.io/pypi/v/mkdocs-placeholder-plugin)](https://pypi.org/project/mkdocs-placeholder-plugin/)
![License](https://img.shields.io/pypi/l/mkdocs-placeholder-plugin)
![Python versions](https://img.shields.io/pypi/pyversions/mkdocs-placeholder-plugin)

This plugin allows you to have placeholders in your site, that can be dynamically replaced at runtime using JavaScript (see [demo page](https://mkdocs-placeholder-plugin.six-two.dev/demo/)).


## Documentation

This README is just a short intro to the package.
For a quick start and detailed information please see the [documentation for the last release](https://mkdocs-placeholder-plugin.six-two.dev/).
The documentation is also available in the `docs` folder of the source code and can be built locally with [MkDocs](https://www.mkdocs.org/).

## Development version

If you want to use the latest development version (may be broken/buggy from time to time), you can install it by:

1. Cloning the repository:
    ```bash
    git clone https://github.com/six-two/mkdocs-placeholder-plugin
    cd mkdocs-placeholder-plugin
    ```
2. Building/Downloading the JavaScript files.
    Choose any of the following ways:
    
    - Build it with npm (natively), by running the `./build-docs.sh` script.
    - Build it in a (docker/podman) container by using the `Dockerfile` in the `typescript` directory.
        The whole thing can be done by running the `buils.sh` script in the root directory:
        ```bash
        ./build.sh
        ```
        Once you see mkdocs running, you can terminate it with `Ctrl-C`.
    - Downloading the files from the development version of the documentation (hosted and built by Vercel):
        ```bash
        curl https://dev.mkdocs-placeholder-plugin.six-two.dev/placeholder.min.js -o src/mkdocs_placeholder_plugin/assets/placeholder.min.js
        curl https://dev.mkdocs-placeholder-plugin.six-two.dev/placeholder.min.js.map -o src/mkdocs_placeholder_plugin/assets/placeholder.min.js.map
        ```
3. Installing the package with pip:
    ```bash
    python3 -m pip install .
    ```

The corresponding documentation is hosted at <https://dev.mkdocs-placeholder-plugin.six-two.dev>.

## Notable changes

### Version 0.5.0

- Added inline editable placeholders (see [#6](https://github.com/six-two/mkdocs-placeholder-plugin/issues/6)) and enabled them by default:
    - If you want to disable them by default, add `inline_editors: false` to the `settings` attribute in your `placeholder-plugin.yaml`.
    - If you want to disable them and prevent users from enabling them, add `normal_is_alias_for: dynamic` to the `settings` attribute in your `placeholder-plugin.yaml`.
    - You can choose how inline placeholders look via the [`inline_editor_style` setting](https://mkdocs-placeholder-plugin.six-two.dev/configuration/#inline_editor_style).
- You can now embed the placeholder settings editor anywhere if your page with `<div class="placeholder-settings-panel"></div>`.

### Version 0.4.1

- Validators can copy rules from other validators via the `import_rules_from` attribute
- New validators: `email`, `linux_interface`, `mac_address`, `uuid`

### Version 0.4.0

- Configuration format changed:
    - Validators are no longer defined in-line and instead defined in a `validators` section -> easier to reuse custom validators.
    - Placeholders now need to be specified in a `placeholders` section.
    - Most settings are now in the configuration file instead of in your `mkdocs.yml`.
- Some actions can now be toggled by visitors of the site. The settings open when you click the gear icon on a (dynamic) placeholder input table.
- (By default) values are saved when the focus leaves a text field.
- Removed static placeholder input tables (`<placeholdertable>`).
- Uncoupled the code from MkDocs.
    You should now be able to relatively easy port the project to other Markdown based static site generators if you want to.

### Version 0.3.1

- Removed `Apply all changes` buttons. See [issue #3](https://github.com/six-two/mkdocs-placeholder-plugin/issues/3)

### Version 0.3.0

This release may be a bit buggy due to the rewrite and the documentation is not entirely accurate yet.
I will update the docs after I also clean up / rewrite the python code (planed for v0.4.0).

- Rewrote the JavaScript code in TypeScript:
    - Packed and minified using Webpack, so the file is a bit smaller
    - Should find stupid errors I make in code paths that I do not test (often)
    - Sophisticated update logic: Instead of always reloading the page it tries to update the DOM in-place (if possible), which should improve user experience a bit and is much faster
    - Nested placeholders (placeholders that contain placeholders that contain placeholder...) no longer need to be specified in a speific order in the configuration file.
    - A placeholder's `default-function` and a validator rule's `match_function` are now evaluated using [`new Function(...)`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function) instead of `eval(...)`, so you need to add a return statement.

### Version 0.2.5

- When an JavaScript generated `auto-input-table` is empty, now a info box is shown (instead of nothing / an empty table).
- Bugfixes:
    - `auto_placeholder_tables_javascript` had no effect.
    - Pressing `Enter` on text fields without validators did not try to reload the page,

### Version 0.2.4

- Added input validation:
    - Predefined types: `domain`, `file_name_linux`, `file_name_windows`, `hostname`, `ipv4_address`, `ipv4_range_cidr`, `ipv4_range_dashes`, `ipv6_address`, `path_linux`, `path_windows`, `port_number`, `url_any`, `url_http`
    - Custom validators with rules that either use `regex` or `match_function`
- Added `placeholder_extra_js` field to plugin configuration (for loading custom functions)
- Added `default-function` attribute for placeholders

### Version 0.2.3

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

## Process for releases

This is just for me :)

1. Run linters:
    ```bash
    mypy src
    ```
    ```bash
    pyflakes src
    ```

    Check npm code with podman:
    ```bash
    podman run -it --rm --workdir /typescript -v "$(pwd)/typescript:/typescript" localhost/placeholder-npm:latest npm run lint
    ```

    Or with docker:
    ```bash
    docker run -it --rm --workdir /typescript -v "$(pwd)/typescript:/typescript" placeholder-npm:latest npm run lint
    ```
2. Update the changelog in this README file.
3. Update version number in `./setup.cfg` and `typescript/src/api.ts`.
4. Disable `debug_javascript` in `placeholder-plugin.yaml`.
5. Build and update package.
6. Create a commit for the release (`Version 0.X.Y`) and push it.
7. Add a tag named `0.X.Y`:
    ```bash
    git tag 0.X.Y
    ```
8. Update the `latest-release` branch, so that the documentation website gets updated:
    ```bash
    git branch --force latest-release HEAD
    git push --tags origin latest-release
    ```

### Updating python dependencies

If you don't have them, install `pip-tools`:
```bash
python3 -m pip install pip-tools
```

Then update `requirements.txt`:
```bash
pip-compile -U
```

### Updating npm dependencies

These are only used for the build process, so keeping them up to date is not that critical.

Start a container with nodeJS:
```bash
podman run -it --rm -v "$(pwd)/typescript:/mnt" node:latest bash
```

In the container run the following commands to update the `typescript/package*.json` files on the host:
```bash
cd /mnt
npm i -g npm-check-updates
ncu -u
npm i --package-lock-only
```

Then rebuild the docker image on the host:
```bash
cd typescript/
podman build --tag placeholder-npm .
```

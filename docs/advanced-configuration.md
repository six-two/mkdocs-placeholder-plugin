# Configuration

## Plugin settings

Option | Type | Default value
---|---|---
add_apply_table_column | `bool` | `False`
enabled | `bool` | `True`
placeholder_file | `str` | placeholder-plugin.yaml
placeholder_js | `str` | assets/javascripts/placeholder-plugin.js
reload_on_change | `bool` | `True`
replace_delay_millis | `int` | 0
show_warnings | `bool` | `True`
static_pages | `list[str]` | `[]` (empty list)
table_default_show_readonly | `bool` | `False`
table_default_type | `str` | simple

You can set these values in `mkdocs.yml` like this:

```yaml
plugins:
- placeholder:
    add_apply_table_column: False
    enabled: True
    placeholder_file: placeholder-plugin.yaml
    placeholder_js: assets/javascripts/placeholder-plugin.js
    reload_on_change: True
    replace_delay_millis: 0
    show_warnings: true
    static_pages:
    - static_replacements/index.html
    - another-page.html
    table_default_show_readonly: False
    table_default_type: simple
```

### add_apply_table_column

Add a table column at the end of placeholder input tables that will reload the page when clicked.
May be useful, when you disable `reload_on_change`.

### enabled

When you set this to false, the extension will be disabled.
This allows you to for example conditionally disable this plugin if a specific environment variable is used.

### placeholder_file

The placeholders and their initial values will be read from this file.

### placeholder_js

The path where to store the JavaScript file created by this plugin.
If this file already exists, the plugin will not change its contents.
This allows you to modify the JavaScript code used by this plugin if you have a reason to ever want to do that.

### reload_on_change

This will cause the page to be reloaded (and thus upload the placeholder values), when a one of the following events occurs:

- For a checkbox: when the value is changed
- For a dropdown menu: when a different value is selected
- For a textbox: when the `Enter` key is pressed

### replace_delay_millis

This value determines, *when* the replacement should be triggered:

- `x` < 0: Replace the placeholders as soon as the script is executed. I need this to make replacements in Mermaid diagrams work.
- `x` == 0: Replace the placeholders as soon as the `document.onload` event is fired (when the page is fully loaded). This is the current default value.
- `x` > 0: After the `document.onload` event is fired, wait `x` milli seconds, then replace the placeholders.

### show_warnings

This plugin will print warnings if it detects potential errors like:

- Input fields that are linked to a not defined variable name
- Variable names that do not match the recommended naming conventions/format

If you know what you are doing and these warinings annoy you, you can disable them with `whow_warnings: false`.

### static_pages

Pages where placeholders will be replaced at build time by the predefined values.
Input fields for variables will be disabled on these pages.
It takes a list of glob placeholders, so something like `relative/path/**/*.html` should also work.

!!! warning
    This code is run after the pages are processed, so the path you need to specify is not the same as the one of the markdown file.
    So `page.md` will either be `page.html` or `page/index.html`.

### table_default_show_readonly

The default value for placeholder input tables, when no `show-readonly` attribute was specified.

### table_default_type

The default value for placeholder input tables, when no `type` attribute was specified.

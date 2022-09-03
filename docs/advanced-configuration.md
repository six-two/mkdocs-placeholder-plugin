# Configuration

## Plugin settings

Option | Type | Default value
---|---|---
show_warnings | `bool` | `True`
static_pages | `list[str]` | `[]` (empty list)
placeholder_file | `str` | placeholder-plugin.yaml
placeholder_js | `str` | assets/javascripts/placeholder-plugin.js
replace_delay_millis | `int` | 0

You can set these values in `mkdocs.yml` like this:

```yaml
plugins:
- placeholder:
    show_warnings: true
    static_pages:
    - static_replacements.md
    placeholder_file: placeholder-plugin.yaml
    placeholder_js: assets/javascripts/placeholder-plugin.js
    replace_delay_millis: 0
```


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

### placeholder_file

The placeholders and their initial values will be read from this file.

### placeholder_js

The path where to store the JavaScript file created by this plugin.
If this file already exists, the plugin will not change its contents.
This allows you to modify the JavaScript code used by this plugin if you have a reason to ever want to do that.

### replace_delay_millis

This value determines, *when* the replacement should be triggered:

- `x` < 0: Replace the placeholders as soon as the script is executed.
- `x` == 0: Replace the placeholders as soon as the `document.onload` event is fired (when the page is fully loaded). This is the current default value.
- `x` > 0: After the `document.onload` event is fired, wait `x` milli seconds, then replace the placeholders.

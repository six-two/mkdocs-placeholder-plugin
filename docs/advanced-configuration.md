# Configuration

## Plugin settings

Option | Type | Default value
---|---|---
show_warnings | `bool` | `True`
placeholder_file | `str` | placeholder-plugin.yaml
placeholder_js | `str` | assets/javascripts/placeholder-plugin.js

You can set these values in `mkdocs.yml` like this:

```yaml
plugins:
- placeholder:
    show_warnings: true
    placeholder_file: placeholder-plugin.yaml
    placeholder_js: assets/javascripts/placeholder-plugin.js
```


### show_warnings

This plugin will print warnings if it detects potential errors like:

- Input fields that are linked to a not defined variable name
- Variable names that do not match the recommended naming conventions/format

If you know what you are doing and these warinings annoy you, you can disable them with `whow_warnings: false`.

### placeholder_file

The placeholders and their initial values will be read from this file.

### placeholder_js

The path where to store the JavaScript file created by this plugin.
If this file already exists, the plugin will not change its contents.
This allows you to modify the JavaScript code used by this plugin if you have a reason to ever want to do that.

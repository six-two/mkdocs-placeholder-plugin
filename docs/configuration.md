# Configuration

## Plugin settings

These settings are specified in your MkDocs configuration file (by default `mkdocs.yml`).

Option | Type | Default value
---|---|---
enabled | `bool` | `True`
js_output_dir | `str` | `assets/javascripts/`
placeholder_css | `str` | `assets/javascripts/placeholder-plugin.css`
placeholder_extra_js | `str` | empty string
placeholder_file | `str` | `placeholder-plugin.yaml`

You can set these values like this:

```yaml title="mkdocs.yml"
plugins:
- placeholder:
    enabled: True
    js_output_dir: assets/javascripts/
    placeholder_css: assets/javascripts/placeholder-plugin.css
    placeholder_extra_js: ""
    placeholder_file: placeholder-plugin.yaml
```


### enabled

When you set this to false, the extension will be disabled.
This allows you to for example conditionally disable this plugin if a specific environment variable is used.

### js_output_dir

The directory where the JavaScript files will be written to.
It should not contain any files with the following names, since they may be overwritten by the plugin:

- `placeholder.min.js`
- `placeholder.min.js.map`
- `placeholder-data.js`
- `placeholder-combined.js`

### placeholder_css

The path to the file, where the plugin will write its CSS (cascading style sheets) code to.
There are three different setups you can do:

1) Point it to an existing file with CSS code.
    In this case the plugin will append its own code (leaving your code in place) and ensure that the file is sourced.
    You can use this to add custom styling for placeholder elements.
2) Point to an empty / non-existent file.
    In this case the plugin will create the file and fill it with the default styling.
3) Specify an empty string (`""`).
    In this case the plugin will *not* provide any styles, so you have total control over (and responsibility for) the visual representation of placeholders, input fields, automatic input tables, etc. 

CSS file. If it exists, the contents will be appended to. add empty string to not include the default styles

### placeholder_extra_js

This file will be read and inserted into the JavaScript file created by the plugin.
It will be loaded before the plugin is run, so you can use it to supply custom JavaScript functions for use with the plugin (for example used as a `default-function` in a placeholder).

### placeholder_file

The placeholders, validators, and MkDocs independent settings (see next section) will be read from this file.
This path should be either relative to the root of the directory or relative to the MkDocs configuration file.
Usually both values are the same, except when you do something like this:

```bash
mkdocs gh-deploy --config-file ../my-mkdocs-project/mkdocs.yml --remote-branch master
```



## Placeholder settings

These settings are specified in your placeholder configuration file (by default `placeholder-plugin.yaml`).

Option | Type | Default value
---|---|---
apply_change_on_focus_change | `bool` | `True`
auto_placeholder_tables | `bool` | `True`
create_no_js_fallback | `bool` | `True`
debug_javascript | `bool` | `False`
dynamic_prefix | `str` | `d`
dynamic_suffix | `str` | `d`
expand_auto_tables | `bool` | `True`
html_prefix | `str` | `i`
html_suffix | `str` | `i`
normal_prefix | `str` | `x`
normal_suffix | `str` | `x`
replace_delay_millis | `int` | `0`
show_warnings | `bool` | `True`
static_prefix | `str` | `s`
static_suffix | `str` | `s`

You can set these values like this:

```yaml title="placeholder-plugin.yaml"
settings:
    apply_change_on_focus_change: true
    auto_placeholder_tables: true
    create_no_js_fallback: true
    debug_javascript: false
    dynamic_prefix: d
    dynamic_suffix: d
    html_prefix: i
    html_suffix: i
    normal_prefix: x
    normal_suffix: x
    replace_delay_millis: 0
    show_warnings: true
    static_prefix: s
    static_suffix: s
```

### apply_change_on_focus_change

Save and apply values entered into textbox fields when the user changes focus away from the field (presses `Tab`, clicks somewhere else, etc).

### auto_placeholder_tables

When enabled the plugin will add an automatic input table to the top of every page.
You can disable this if you manually want to specify them (or have them at very specific locations).

### create_no_js_fallback

Create fallback values, so that users with browsers where the code does not run (incompatible/very old browser, JavaScript is disabled, ...) will see a somewhat presenatble page filled with the default values (for placeholders, input elements, and input tables).
However, since the JavaScript code does not run, users can not update/change any placeholders and the input fields are diabled.

This creates slightly bigger pages and takes some extra time during the build process, so you can disable it if you feel like that situation will not happen.

### debug_javascript

If enabled, JavaScript debugging messages will be printed to the browsers console.
These include information such as:

- The placeholder / configuration data passed by the plugin to the JavaScript code
- How many input elements of each type were found on the page
- Which placeholders were replaced and approximately how often

If enabled, it will also add the source map file, so that you can see the unminified source code and have more meaningful stack traces.
If disabled, all JavaScript generated by this plugin is merged into a single file instead and no source maps are provided.

### expand_auto_tables

Whether to expand automatic placeholder tables by default.

### \*\_prefix and \*\_suffix

!!! warning "Use with care"
    There are a bunch values ways, that may break your placeholder replacement.
    So please do *not* do any of the following:

    - Use something that will be split up by syntax highlighting in code listings or is modified by the Markdown parser (example: `_NAME_` -> `<i>NAME</i>`).
    - Use both an empty prefix and suffix (`NAME`).
        This may (at the very least) be problematic in combination with placeholder tables.
    - Use characters that have special meanings in regular expressions (`*`, `|`, `.`, `[`, ...).
        While it should work in theory, it may lead to bugs if I forgot to add escaping somewhere.
    - Use empty prefixes / suffixes if you have similarly named variables.
        For example if you have two placeholders called `PASSWORD` and `PASSWORD_ADMIN`, you will run into troubles if you do not use a suffix (`<prefix>PASSWORD_ADMIN` may become `<ValueOfPASSWORD>_ADMIN`).
    
    My recommendation is to both use a suffix and a prefix and make them only contain lowercase characters and underscores (like `var_NAME_html`).

This defines the pattern that will be used to detect when you want to replace a placeholder (and with what replacement method).
When replacing placeholders, the site is searched for the following pattern: `<prefix><placeholder_name><suffix>`.
For example if you use `normal_prefix: var_` and `normal_suffix: n`, then placeholders will need to use the format `var_NAMEn` instead of `xNAMEx`.


### replace_delay_millis

This value determines, *when* the replacement should be triggered:

- `x` < 0: Replace the placeholders as soon as the script is executed. I need this to make replacements in Mermaid diagrams work.
- `x` == 0: Replace the placeholders as soon as the `document.onload` event is fired (when the page is fully loaded). This is the current default value.
- `x` > 0: After the `document.onload` event is fired, wait `x` milli seconds, then replace the placeholders.

### show_warnings

This plugin will print warnings if it detects potential errors like:

- Input fields that are linked to a not defined variable name.
- Variable names that do not match the recommended naming conventions/format.

If you know what you are doing and these warnings annoy you, you can disable them with `show_warnings: false`.

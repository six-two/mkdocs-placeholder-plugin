# Advanced usage

## Placeholder attributes

You can set some extra attributes for placeholders:

Option | Type | Default value
---|---|---
allow_nested | `bool` | depends on type and if it is read only
default | `str` | N/A
default-function | `str` | N/A
description | `str` | empty string
read_only | `bool` | `False`
replace_everywhere | `bool` | `False`
validators | `list[str]` | empty list
values | `dict[str,str]` | N/A


Examples:

```yaml
FIRST_NAME:
  default: John
  description: What should I call you?
  read_only: false
  replace_everywhere: false
```

```yaml
RANDOM:
  default-function: "return Math.floor(Math.random()*100);"
  description: A random number between 0 and 99
```

### allow_nested

When set to `true` this allows placeholder substitution in the value of this placeholder.
By default this is enabled for all placeholders, where users can not choose arbitrary values (checkboxes, dropdown menus, and readonly text fields).

### default / default-function

!!! note "Mutually exclusive"

    `default` and `default-function` are mutually exclusive.
    You have to specify **exactly one** of them to provide a default value.

=== "default"

    This is the value, that is used as the initial value for the placeholder.
    The following two declarations are equivalent:
    ```yaml
    FIRST_NAME: John
    ```

    ```yaml
    FIRST_NAME:
      default: John
    ```

=== "default-function"

    This allows you to specify custom JavaScript code, that will be evaluated if the placeholder is not set.
    It should return a string or something that can easily converted to a string (such as a number).

    If you want to use complex functions that can not be expressed as a one-liner, you can:

    1. Create a javascript file containing your function(s).
        For example this repository has `placeholder-extra.js`:
        ```javascript
        const generate_placeholder_password = (length) => {
            [...]
            return pw_chars.join("");
        }
        ```
    2. In the plugin's configuration within your `mkdocs.yaml`, set the `placeholder_extra_js` property to the path of your file.
        For example:
        ```yaml
        plugins:
        - placeholder:
            placeholder_extra_js: placeholder-extra.js
        [...]
        ```

        While you technically could load your code with other ways (such as MkDocs' `extra_javascript`), this way guarantees that it will be loaded *before* the plugin is run, which other methods may not guarantee.
    3. In your placeholder's definition, set `default-function` to invoke the function with your desired arguments:
        ```yaml
        PASSWORD:
          default-function: "return generate_placeholder_password(10)"
          description: A randomly generated password updated anytime you clear your localStorage
        ```

### description

This description can be used in placeholder input tables to describe to users what value is expected for the field.

### read_only

Defaults to `false`.
If this is set to `true`, input field's for the placeholder will be disabled, so that users can not change the placeholder unless they go to the browser's `Developer Tools` and change the `localStorage` object.
Read-only fields can (and by default will) be hidden from placeholder input tables.

### replace_everywhere

Defaults to `false`.
If this is set to `false`, only visible text is replaced, which means that the inner HTML replacement method is not allowed for this placeholder.
If you set it to `true`, it may be replaced anywhere in the page's document object model (probably including scripts, element attributes (such as a link's href), etc) when using the inner HTML replacement method (`iPLACEHOLDER_NAMEi`).

!!! warning "Dangerous - may introduce security vulnerabilities"
    You can very easily create self-XSS vulnerabilities if you set this to `true`.
    These may be chained with other vulnerabilities to allow attackers to potentially steal cookies, redirect to malicious pages and/or perform actions as the user.
    So please use this sparingly, if at all.

    Assuming that you just have a static MkDocs site, the impact should be minimal/none, but please think twice before you enable this.

### validators

Which validators to use to determine what input is acceptable.
Only supported on normal (textbox) placeholders, not on checkbox or dropdown ones.
It would not make sense for them anyways, since the user can only select values that the site's author offers them.
For more information see the [validators page](validators.md).

### values

Used to define checkbox or dropdown menu fields.
See the [usage page](usage.md#checkbox-field).

## Combining fields

Sometimes certain combinations of placeholders are often used.
For example you may have an email address that consists of three different parts:

- first name
- surname
- domain

You can combine them into a single value with the following steps:

1. Add the combined value in your `placeholder-plugin.yaml` and make sure that `allow_nested` is set to `true`;
    Example:

    ```yaml
    placeholders:
      # The variables that are part of the combined value
      FIRST_NAME: John
      SURNAME: Doe
      DOMAIN: example.com
      # The combined value
      EMAIL:
        default: xFIRST_NAMEx.xSURNAMEx@xDOMAINx
        allow_nested: true
    ```

2. Include the new value (`xEMAILx` in this example) anywhere on your page.

Internally the placeholder plugin is using a dependency graph for the placeholders.
Thus, if you were to update `FIRST_NAME`, the `EMAIL` placeholder would also be updated, since it depends on `FIRST_NAME`.
You could even use `xEMAILx` in other variables (say `xMAILING_LISTx`).
The only thing you should not do are recursive placeholders (placeholders referencing themselves) or dependency loops (A contains B contains C contains A).
These can will lead to errors, since expanding them would result in a infinite loop.

If you want to hide these fields in placeholder input tables, add the `read_only` field and set it to `true`.
In this case you do not explicitly need to set `allow_nested`, since it is enabled by default for readonly placeholders:

```yaml
EMAIL:
  default: xFIRST_NAMEx.xSURNAMEx@xDOMAINx
  read_only: true
```


## Placeholder input tables

Placeholder tables using the `<placeholdertable>` tag were removed in version 0.4.0.
For normal tables see the [usage](./usage.md) page.

## Custom styling

You can see the default style in `src/mkdocs_placeholder_plugin/generic/generic_style.py`.
The following are some common classes you may want to restyle.

Class name | Element
---|---
`placeholder-value` | All placeholders, both with and without inline editors
`inline-editor-requested` | Placeholder which will be assigned an inline editor, unless they are disabled by the user settings
`placeholder-value-static` | Placeholders without inline editors
`placeholder-value-checkbox` | Checkbox placeholder with inline editor
`placeholder-value-dropdown` | Dropdown placeholder with inline editor
`placeholder-value-editable` | Textbox placeholder with inline editor
`input-for-variable` | (non-inline) input element for an placeholder
`validation-none` | Inline editors and input elements without a validator
`validation-ok` | Inline editors and input elements that pass validation successfully
`validation-warn` | Inline editors and input elements that pass validation with warnings
`validation-error` | Inline editors and input elements that fail validation because of errors
`value-modified` | Inline editors and input elements for a textbox placeholder that has been modified and not yet saved

To overwrite the default rules, define a more specific rule by specifying that it applies only to span elements like the following:
```css
span.placeholder-value-static {
    color: black;
}
```

Some other values you may want to overwrite are:

- `span.placeholder-value-*:empty`: The placeholder shown when an inline editor has an empty value.
    By default it is just a pink square.
- `span.placeholder-value-*:hover`: Style when a user moves their mouse pointer over an inline editor.

### Highlighting placeholders

You may want to show users, which values they can change via the input boxes.
To do this, you can style the wrapper inserted by the dynamic replacement method.
Since the wrapper has the class `placeholder-value`, you can add styling for it like this:

```css
span.placeholder-value {
    background-color: yellow;
}
```

If you enable the JavaScript debug mode, you will automatically get the placeholders highlighted in gray.
If you do not like that, you can undo the styling by overwriting it with more specific rules.
You can find the debug highlight rules in the variable `HIGHLIGHT_STYLE` in `src/mkdocs_placeholder_plugin/style.py`.

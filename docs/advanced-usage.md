# Advanced usage

## Placeholder attributes

You can set some extra attributes for placeholders:

```yaml
FIRST_NAME:
    default: John 
    description: What should I call you?
    read_only: false
    replace_everywhere: false
```

### default

This is the value, that is used as the initial value for the placeholder.
The following two declarations are equivaluent:
```yaml
FIRST_NAME: John
```

```yaml
FIRST_NAME:
    default: John 
```

### description

This description can be used in placeholder input tables to describe to users what value is expected for the field.

### read_only

Defaults to `false`.
If this is set to `true`, input field's for the placeholder will be disabled, so that users can not change the placeholder unless they go to the browser's `Developer Tools` and change the `localStorage` object.
Read-only fields can (and by default will) be hidden from placeholder input tables.

### replace_everywhere

Defaults to `false`.
If this is set to `false`, only visible text is replaced.
If you set it to `true`, it may be replaced anywhere in the page's document object model (probably including scripts, element attributes (such as a link's href), etc).

!!! warning "Dangerous - may introduce security vulnerabilities"
    You can very easily create self-XSS vulnerabilities if you set this to `true`.
    These may be chanied with other vulnerabilities to allow attackers to potentially steal cookies, redirect to malicious pages and/or perform actions as the user.
    So please use this sparringly, if at all.

    Assuming that you just have a static MkDocs site, the impact should be minimal/none, but please think twice before you enable this.

## Combining fields

Sometimes certain combinations of placeholders are often used.
For example you may have an email address that consists of three different parts:

- first name
- surname
- domain

You can combine them into a single value with the following steps:

1. Add the combined value in your `placeholder-plugin.yaml` *before* the lines that define the placeholders used in the expression;
    Example:

        # This one needs to be specified first, since it includes the other variables
        EMAIL: xFIRST_NAMEx.xSURNAMEx@xDOMAINx
        # The variables that are part of the combined value
        FIRST_NAME: John
        SURNAME: Doe
        DOMAIN: example.com

2. Include the new value (`xEMAILx` in this example) anywhere on your page.

This works because variables are replaced in the order they are defined.
So `xEMAILx` will be replaced with `xFIRST_NAMEx.xSURNAMEx@xDOMAINx` and those variables will then be replaced by their respective values.
You could even use `xEMAILx` in other variables (say `xMAILING_LISTx`) that are defined above it.

If you want to hide these fields in placeholder input tables, add the `read_only` field and set it to `true`:

```
EMAIL:
    default: xFIRST_NAMEx.xSURNAMEx@xDOMAINx
    read_only: true
```

## Static replacements

Tries to do build time replacing of placeholders on the pages defined via `static_pages` in the plugin config options.
@TODO: fully document, fix bugs


## Placeholder input tables

### Build time generated

Beginning with version 0.1.3, you can embed input tables for placeholders.
The following syntax is used:

```html
<xPLACEHOLDERTABLEx entries="auto" show-readonly="false" type="simple">
```

None of the attributes are required, so you can also do this:
```html
<xPLACEHOLDERTABLEx>
```

The following attributes are available:

- `entries` can have the following values:
    - `auto`: Check which variables are used on the page and list only them in the table. This is the default setting if the attribute is not set.
    - `all`: Use all placeholders in the table.
    - `PLACEHOLDER_1,PLACEHOLDER_2,[...]`: Only show the specified placeholders in the table.
- `show-readonly` determines, if placeholders with `read_only: true` will be shown. This is for example useful to hide *combined fields* described above. Defaults to the value specified in the config (or `False`).
- `type` determines, which columns are included in the table:
    - `simple` shows `Name` and `Input`
    - `description` shows `Name`, `Input` and `Description`
    - You can manually define the columns to use, by separating them with a comma.
        Example: `input,description`

        Valid column names are:

        - description
        - input
        - name
        - value

    It defaults to the value specified in the config (or `simple`).


Since these tables are generated at build time, they are not entirely accurate, if you have conditional placeholders that are only included with some checkbox/dropdown values selected.
The tables will also be indexed by the search plugin, so they may spam your search results, especially if you include the description column.

### Dynamically generated

Starting with version 0.2.2 you can add the following tag into your page:
```html
<div class="auto-input-table" data-columns="name,description,input"></div>
```

These tags will be detected by the JavaScript.
Then a row for each placeholder, that was actually used on the site will be generated and added as children to the element.
Currently only limited features are supported (no support for `reload_on_change` and `add_apply_table_column`, etc).


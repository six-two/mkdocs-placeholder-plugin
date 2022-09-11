# Advanced usage

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

Beginning with version 0.1.3, you can embedd input tables for placeholders.
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
    - `simple` shows `Varibale` and `Value`
    - `description` shows `Varibale`, `Value` and `Description`

    It defaults to the value specified in the config (or `simple`).




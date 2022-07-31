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

## Static replacements

**To be implemented.**
May be useful for print page.

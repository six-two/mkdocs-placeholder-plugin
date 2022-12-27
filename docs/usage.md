# Usage

## Installation

You can install this plugin with pip:
```bash
python3 -m pip install mkdocs-placeholder-plugin
```

## Configuration

### Register plugin

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
  - search
  - placeholder
```

> If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set.

More information about plugins in the [MkDocs documentation](http://www.mkdocs.org/user-guide/plugins/).

### Defining placeholers

Add a `placeholder-plugin.yaml` in the root of your MkDocs project and define the placeholder names and initial values here.
For example:

```
NAME: John Doe
PLUGIN: MkDocs Placeholder Plugin
RATING: great
YEAR: 2022
RANDOM: 5
```

Ideally you only use capital letters and underscores in your placeholders.
Other characters may be interpreted as markdown syntax or lead to syntax highlighting splitting the placeholder.
If that happens, the placeholder replacement will fail.
Leading and trailing underscores should not be used, since they are reserved for future features.

## Using placeholders

Now you can use the placeholders you defined using the following `xPLACEHOLDER_NAMEx` format.
Example text:

```markdown
Hi, I am xNAMEx and I think that xPLUGINx is xRATINGx!
```

## Changing placeholder values


### User input field

You can create an input field (that will change a placeholder's value) with the following syntax:

```html
<input data-input-for="PLACEHOLDER_NAME">
```

For example:

```html
<label>Your name: <input data-input-for="NAME"></label>
```

All inputs tagged this way will get assigned the class `input-for-variable`, so that you can more easily style them with CSS.
This works for the normal textbox fields and special types (checkbox, dropdown).

#### Textbox field

Unless otherwise specified, the input field will be a regular textbox that allows the user to specify arbitrary values.
So for example if you have the following in your `placeholder-plugin.yaml`, the input field will be a textbox:

```yaml
LINK: 
  default: https://www.example.com/test/page
```

The `default` field's value will be used as the default for the placeholder.

<label>Example: <input data-input-for="LINK"></label>

#### Checkbox field

You can also define placeholders that have only two different values.
They can be respresended by a check box.

You can define them in your `placeholder-plugin.yaml` like this:
```yaml
QUOTE_CHECKBOX:
  description: Use double quotes?
  default: checked
  values:
    checked: "\""
    unchecked: "'"
```

You can use the placeholder's value as you can use any other placeholder.
If the checkbox is checked, the value defined under `values.checked` is used.
Otherwise `values.unchecked` is used.
To determine, whether it is checked by default, you set `default` to `checked` or `unchecked`.
If `default` is not specified or empty, `unchecked` is used.

<label>Example: <input data-input-for="QUOTE_CHECKBOX"></label>


#### Dropdown field

Dropdown fields allow the user to select one of a list of predefined options.
They are defined like this:

```yaml
DROPDOWN:
  description: An test dropdown for selecting your favourite DNS lookup tool
  default: "DNS lookup with host"
  values:
    "DNS lookup with dig": "dig"
    "DNS lookup with nmap": "nmap -n --resolve-all"
    "DNS lookup with host": "host"
    "DNS lookup with nslookup": "nslookup"
```

The possible values are defined in `values`: Each key specifies the displayed option's text, while the value will be assigned to the placeholder.
You can specify the option to select by default, by passing the corresponding display name to `default`.
If this is not done, the first option will be selected by default.

<label>Example: <input data-input-for="DROPDOWN"></label>


### Via JavaScript

You can update the values of placeholders at any time by changing the values in the `localStorage`:

```html
<script>
localStorage.setItem("YEAR", ""+new Date().getFullYear());
</script>
```

Sometimes you may also want a random value, that stays the same after it is set.
This can be implemented like this:

```html
<script>
if (!localStorage.getItem("RANDOM")) {
    localStorage.setItem("RANDOM", ""+Math.floor(Math.random() * 100));
}
</script>
```

This is possible, since the plugin (unless configured otherwise) will only run when the web page is fully loaded (it is waiting for the `window.onload` event).
If a value is set by that time, it will **not** be overwritten. Only when no value is set previously, the default value will be set.

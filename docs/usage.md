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
Your name: <input data-input-for="NAME">
```

All inputs tagged this way will get assigned the class `input-for-variable`, so that you can more easily style them with CSS.

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

This is possible, since the plugin will only run when the web page is fully loaded (it is waiting for the `window.onload` event).
If a value is set by that time, it will **not** be overwritten. Only when no value is set previously, the default value will be set.

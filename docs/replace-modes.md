# Replace modes

Replace modes define how placeholders are replaced in the page via the JavaScript code.
Usually you will only need the default placeholders (`xPLACEHOLDER_NAMEx`), but you can use the other ones as well.
You can mix and match them as you like on any page.
However be advised, that some types do not support dynamic reloading, so the whole page would need to be reloaded if the placeholder (or any placeholder its value contains) are changed.

## Available modes

### Normal

|Default pattern|xPLACEHOLDER_NAMEx|

Unless there is a good reason to use something else, you should probably default to using this.
Currently just is an alias for dynamic, but may change in the future.

### InnerHTML

|Default pattern|iPLACEHOLDER_NAMEi|
|Change requires reload|true|
|Replace locations|anywhere (whole DOM)|
|Safe|false|

Replaces the element **anywhere** in the pages HTML (inside inline scripts, inline styles, HTML tags and attributes, etc).
May lead to cross-site scripting attacks and other problems if you use it.
To allow this, you need to set `replace_everywhere: true` for all placeholders, that use this feature.


### Dynamic

|Default pattern|dPLACEHOLDER_NAMEd|
|Change requires reload|false|
|Replace locations|text nodes|
|Safe|true|

Replaces element with a placeholder wrapper.
This enables updating the element in-place and is necessary if you want to highlight the placeholders.

### Direct / Static

|Default pattern|sPLACEHOLDER_NAMEs|
|Change requires reload|true|
|Replace locations|text nodes|
|Safe|true|

Replaces element directly.

## Nesting

If you have a placeholder that contains another placeholder (and `allow_nested` is `true` for it), the value of the placeholder will be resolved, before it is written to the page.
This may cause the page to reload when you did not expect it.

### Example
You have an element, that uses the InnerHTML or Direct method, and it references a dynamic placeholder.
If you now change the value of the dynamic placeholder, the whole page needs to be reloaded.
Why? Because the change triggered the change of the outer placeholder, that needs a reload to replace the page.

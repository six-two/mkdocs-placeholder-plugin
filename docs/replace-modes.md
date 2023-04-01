# Replace modes

Replace modes define how placeholders are replaced in the page via the JavaScript code.

## Available modes

### InnerHTML

|Change requires reload|true|
|Replace locations|anywhere (whole DOM)|
|Safe|false|

Replaces the element **anywhere** in the pages HTML (inside inline scripts, inline sytles, HTML tags and attributes, etc).
May lead to cross-site scripting attacks and other problems if you use it.


### Dynamic

|Change requires reload|false|
|Replace locations|text nodes|
|Safe|true|

Replaces element with a placeholder wrapper.
This enables updating the element in-place and is necessary if you want to highlight the placeholders.

### Direct / Static

|Change requires reload|true|
|Replace locations|text nodes|
|Safe|true|

Replaces element directly.

### Normal

Currently just is an alias for dynamic, but may change in the future.

## Nesting

If you have a placeholder that contains another placeholder (and `allow_recursive` is `true` for it), the value of the placeholder will be resolved, before it is written to the page.
This may cause the page to reload when you did not expect it.

### Example
You have an element, that uses the InnerHTML or Direct method, and it references a dynamic placeholder.
If you now change the value of the dynamic placeholder, the whole page needs to be reloaded.
Why? Because the change triggered the change of the outer placeholder, that needs a reload to replace the page.

# Replace modes

Replace modes define how placeholders are replaced in the page via the JavaScript code.

## InnerHTML

|Change requires reload|true|
|Replace locations|anywhere (whole DOM)|
|Safe|false|

Replaces the element **anywhere** in the pages HTML (inside inline scripts, inline sytles, HTML tags and attributes, etc).
May lead to cross-site scripting attacks and other problems if you use it.


## Dynamic

|Change requires reload|false|
|Replace locations|text nodes|
|Safe|true|

Replaces element with a placeholder wrapper.
This enables updating the element in-place and is necessary if you want to highlight the placeholders.

## Direct / Static

|Change requires reload|true|
|Replace locations|text nodes|
|Safe|true|

Replaces element directly.

## Normal

Currently just is an alias for dynamic, but may change in the future.

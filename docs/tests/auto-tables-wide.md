# Tests: Automatic input tables with wide input boxes

<button class="md-button md-button--primary" onclick="PlaceholderPlugin.debug_disable_reload()">Debug: Disable page reload</button>

<style>
.auto-input-table input,
.auto-input-table select {
    width: 50em;
}
</style>

This page shows how you can have extra wide placeholder to easily hold values like `Rindfleischetikettierungsgesetz` or `MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM`. Add styling like the following to your custom CSS:
```css
.auto-input-table input,
.auto-input-table select {
    width: 50em;
}
```

## Generated with JavaScript

If you have more columns than by default, then the contents will likely be off-screen.

<div class="auto-input-table" data-columns="name,input,value,description"></div>

### Second table

It is also generated with JavaScript:

<div class="auto-input-table" data-columns="description-or-name,input"><b>You should see this text instead of a fallback table</b></div>

### Placeholders

xXSS_DROPDOWN_ALLx

xVALIDATOR_IPV4_ADDRESSx

xVALIDATOR_FILE_WINDOWSx

## Manual inputs

IP4 Address:<br>
<input class="some-custom-class-for-styling" data-input-for="VALIDATOR_IPV4_ADDRESS">

Windows File name:<br>
<input class="some-custom-class-for-styling" data-input-for="VALIDATOR_FILE_WINDOWS">


<style>
.some-custom-class-for-styling {
    width: 100%;
}
</style>


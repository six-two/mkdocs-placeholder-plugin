# Intro

I|github|six-two/mkdocs-placeholder-plugin|
I|pypi|mkdocs-placeholder-plugin|
L|Documentation|https://mkdocs-placeholder-plugin.six-two.dev/|

This plugin allows you to use placeholders in your website that can be dynamically updated.

## Features

- Easy to create input fields for users to change placeholder values.
- Uses localStorage, so you (probably) don't need a cookie banner. Data will persist across visits unless the user's browser is configured to clear the data (private browsing mode)
- You can automatically add inputs for all placeholders used on a page.
- You can edit values directly in the page (inline editors).


## Versioning

Generally, smaller version updates (for example `0.2.4` -> `0.2.5`) can contain new features and bug fixes that do not *significantly* break backwards compatibility.
Minor version updates (`0.1.X` -> `0.2.0`) will have significant breaking changes, so you will want to check the [changelog](https://github.com/six-two/mkdocs-placeholder-plugin#notable-changes) before updating.
You should probably also use version pinning to make sure that you do not install new versions (without checking that they do not break your config first).

### Migrating 0.3.x -> 0.4.0

You will need to make some adjustments to your `mkdocs.yml` and `placeholder-plugin.yaml`:

1. Open `mkdocs.yml` and comment out all of this plugin's settings except for the ones specified in [Configuration > Plugin Settings](./configuration.md#plugin-settings).
2. Open `placeholder-plugin.yaml`, indent all lines, and add `placeholders:` to the top of the file.
3. If you use custom validators, create a `validators:` section in `placeholder-plugin.yaml`, paste your existing validators there, and reference them in the placeholders you copied them from (see [Validators > Custom validators > Example](./validators.md#example_1))
4. Search your docs for `<placeholdertable`.
    Replace any such tags either with manually created tables or the following:
    ```html
    <div class="auto-input-table" data-hide-empty data-columns="description-or-name,input"></div>
    ```
5. Optional: Check [Configuration > Placeholder settings](./configuration.md#placeholder-settings) for any settings you have commented out in step 1 and put them in a `settings:` section in `placeholder-plugin.yaml`.

## Interested?

Then click `Next` or use the search function (in the top right corner) to learn more.
If you want to play around a bit, check out the [demo page](demo.md).
You can also checkout the source code of the plugin and this site at the [Github repository](https://github.com/six-two/mkdocs-placeholder-plugin).

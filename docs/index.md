# Intro

I|github|six-two/mkdocs-placeholder-plugin|
I|pypi|mkdocs-placeholder-plugin|
L|Documentation|https://mkdocs-placeholder-plugin.six-two.dev/|

This plugin allows you to use placeholders in your website, that can be dynamically updated.

## Features

- Easy to create input fields for users to change placeholder values.
- Uses localStorage, so you (probably) don't need a cookie banner. Data will persistent across visits unless the user's browser is configured to clear the data (private browsing mode)
- You can dynamically alter placeholder values using JavaScript.
- You can automatically add inputs for all placeholders used on a page.

## Caveats

- By default only visible text is replaced. You can replace placeholders everywhere (for example in link targets) but I haven't used that in practice, so it may be buggy.
- To update the value of a placeholder, the site needs to be refreshed.
    While this (by default) is done automatically, users may notice a small flickering / text changing when this is done.
    If this is unacceptable to you, you can disable the automatic reload and do one of the following:

    - Put the placeholders on a different page than the content that uses them.
    - Add a manual `Reload`/`Apply changes` button below the placeholders, that will execute `window.location.reload()` when clicked.


## Versioning

Generally smaller version updates (for example `0.2.4` -> `0.2.5`) can contain new features and bug fixes that do not *significantly* break backwards compatibility.
Minor version updates (`0.1.X` -> `0.2.0`) will have significant breaking changes, so you will want to check the [changelog](https://github.com/six-two/mkdocs-placeholder-plugin#notable-changes before updating.
You should probably also use version pinning, to make sure that you do not install new versions (without checking that they do not break your config first).


## Interested?

Then click `Next` or use the search function (in the top right corner) to learn more.
You can also checkout the source code of the plugin and this site at the [Github repository](https://github.com/six-two/mkdocs-placeholder-plugin).

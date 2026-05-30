# Supported themes

Personally I prefer MaterialX, so it is the default for this documentation and the best tested.
But the following themes should also work.
You can see this documentation built with each theme by clicking the link:

- [materialX](/): a great theme, the successor to the now deprecated Material for Mkdocs
- [mkdocs](/mkdocs/index.html): default theme of MkDocs, optionally available in properdocs
- [readthedocs](/readthedocs/index.html): builtin theme of MkDocs, optionally available in properdocs

Other themes will likely work too.
If they do not, feel free to fix it (the relevant files are `src/mkdocs_placeholder_plugin/mkdocs/style.py` and maybe `src/mkdocs_placeholder_plugin/generic/generic_style.py`) and submit a [pull request](https://github.com/six-two/mkdocs-placeholder-plugin/pulls).

!!! warning "MaterialX's Instant Loading"
    The instant loading feature of the material theme may cause this plugin to malfunction.

## Known Problems

### highlight.js breaks placeholders in listings

Affects the following themes by default:

- `mkdocs`
- `readthedocs`

Because [highlight.js tries to prevent Cross-Site Scripting (XSS) attacks](https://github.com/highlightjs/highlight.js/wiki/security), it removes the inline HTML that is needed for dynamic placeholders, inline editors and other features.
To work around this, you can disable highlight.js:

```yaml title="mkdocs.yml"
theme:
  name: mkdocs
  highlightjs: false
```

If you want to keep syntax highlighting in code listings, use a different code highlighter such as Pygments:

```yaml title="mkdocs.yml"
markdown_extensions:
  - pymdownx.highlight:
      use_pygments: true
  - pymdownx.superfences
```


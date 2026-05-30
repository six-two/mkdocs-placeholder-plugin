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

# Supported themes

Personally I prefer Material for Mkdocs (`material`), so it is the default for this documentation and the best tested.
But the following themes should also work and you can see this documentation built with that theme by clicking the link:

- [material](/): a great theme ([Homepage](https://squidfunk.github.io/mkdocs-material/))
- [mkdocs](/mkdocs/index.html): default theme of MkDocs
- [readthedocs](/readthedocs/index.html): builtin theme of MkDocs

Other themes will likely work too.
If they do not, feel free to fix it (the relevant files are `src/mkdocs_placeholder_plugin/mkdocs/style.py` and maybe `src/mkdocs_placeholder_plugin/generic/generic_style.py`) and submit a [pull request](https://github.com/six-two/mkdocs-placeholder-plugin/pulls).

!!! warning "Material's Instant Loading"
    The instant loading feature of the material theme may cause this plugin to malfunction.

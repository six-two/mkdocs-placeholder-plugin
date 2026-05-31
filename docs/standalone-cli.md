# Standalone Version

This plugin can also be used with any static site generator.
To do this, create a `placeholder-plugin.yaml` file with all your settings (as you would do with MkDocs too).

In your site generator's configuration, you need to specify some custom CSS and JavaScript files created by the script.
By default they are the following, but you can change then with arguments passed to `markdown-placeholder-standalone` (see `markdown-placeholder-standalone --help` for a list of supported arguments):

Required CSS files:

- `assets/stylesheets/placeholders.css`: Needed to style placeholders, inline editors, etc

Required JavaScript files depend on whether you use `settings.debug_javascript` in your `placeholder-plugin.yaml`:

- With debug mode enabled, you need to include both `assets/javascripts/placeholder.min.js` and `assets/javascripts/placeholder-data.js`.
- Without debug mode, you just need to include `assets/javascripts/placeholder-combined.js`

If you are unsure about the paths, you can also run `markdown-placeholder-standalone` against your HTML files and it will tell you something like the following at the bottom of the output:
```
$ markdown-placeholder-standalone ./site/
[...]
Remember to add 'assets/stylesheets/placeholders.css' as extra_css
Also add 'assets/javascripts/placeholder-combined.js' as extra_javascript
```

After you ran the site generator, you can then run `markdown-placeholder-standalone` against your HTML files directory:
```bash
markdown-placeholder-standalone ./site/
```

If you want to use `placeholder_extra_js` (for example if you migrate from mkdocs and had it in your `mkdocs.yml`), include the desired value as a CLI argument:

```bash
markdown-placeholder-standalone ./site/ --placeholder-extra-js placeholder-extra.js
```

## Split mode

The original MkDocs plugins that ran both on the Markdown files and the HTML files.
During the Markdown phase it searched for placeholders and replaced them with a special internal syntax.
Then during the HTML phase the internal syntax was converted to the actual placeholder HTML.
Running both actions on the HTML files seems to work (at least according to my testing), but it could lead to problems if you used custom placeholder prefixes or suffixes that collide with Markdown syntax.
Say if instead of `xPLACEHOLDER_NAMEx` you decided to use `_PLACEHOLDER_NAME_` or `*PLACEHOLDER_NAME*` or even `<PLACEHOLDER_NAME>`.
All of those would be interpreted as Markdown syntax by your site generator (leading to italics or links) and would no longer be recognizable, when `markdown-placeholder-standalone` searches through the HTML files.
To bypass this issue, you can invoke the `markdown-placeholder-standalone` script both before and after the HTML conversion like this:

```bash
cp path/to/markdown_files path/to/markdown_files.tmp
markdown-placeholder-standalone path/to/markdown_files.tmp/ --phase markdown
# Invoke your site generator here
markdown-placeholder-standalone path/to/html_files/ --phase html
rm -r path/to/markdown_files.tmp
```

You should invoke `markdown-placeholder-standalone path/to/markdown_files/ --phase markdown` on a copy of your Markdown files, as any changes by the plugin will be written back to your files.

const WARNING_HTML = `<div class="admonition warning">
<p class="admonition-title">Development version</p>
<p>This documentation is for the development version of this package, which is the <code>main</code> branch in the GitHub repo.
If you use the pip packages (which you probably do or should do), please check the <a href="https://mkdocs-placeholder-plugin.six-two.dev/">documentation for the latest release</a>.</p>
</div>`

const is_dev_build = window.location.host != "mkdocs-placeholder-plugin.six-two.dev";
console.log("is_dev_build:", is_dev_build);
if (is_dev_build) {
    const content_div = document.querySelector("div.md-content article.md-content__inner.md-typeset");
    const warning_div = document.createElement("div");
    warning_div.innerHTML = WARNING_HTML;
    content_div.insertBefore(warning_div, content_div.firstChild);
    console.log("Inserted:", warning_div);
}

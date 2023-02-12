PlaceholderPlugin.add_default_style = () => {
    const plugin_style = document.createElement('style');
    plugin_style.innerHTML = `
/* Prevent long descriptions from messing up the table too badly */
select.placeholder-dropdown {
    max-width: min(30vw, 200px);
}

table tr td button.placeholder-input-apply-button,input.input-for-variable {
    width: 100%;
}

.input-for-variable {
    border: 2px solid gray;
    border-radius: 3px;
    background-color: var(--md-default-bg-color);
    padding: 5px;
}

.input-for-variable:focus {
    border: 4px solid var(--md-accent-fg-color);
    padding: 3px;
}
`;
// @TODO: try it out with other themes
    document.head.appendChild(plugin_style);
}

if (PlaceholderData.fix_style == true) {
    info("Applied the plugin's CSS (fixes some visual bugs)");
    PlaceholderPlugin.add_default_style();
} else {
    console.warn("Since fix_style is not enabled, you may experience some visaul bugs");
}

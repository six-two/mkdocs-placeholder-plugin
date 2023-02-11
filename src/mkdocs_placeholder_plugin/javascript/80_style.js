PlaceholderPlugin.add_default_style = () => {
    const plugin_style = document.createElement('style');
    plugin_style.innerHTML = `
/* Prevent long descriptions from messing up the table too badly */
select.placeholder-dropdown {
    max-width: min(30vw, 200px);
}
    `;
    document.head.appendChild(plugin_style);
}

if (PlaceholderData.fix_style == true) {
    info("Applied the plugin's CSS (fixes some visual bugs)");
    PlaceholderPlugin.add_default_style();
} else {
    console.warn("Since fix_style is not enabled, you may experience some visaul bugs");
}

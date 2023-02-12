PlaceholderPlugin.add_default_style = () => {
    const plugin_style = document.createElement('style');
    plugin_style.innerHTML = PlaceholderData.custom_css;
    document.head.appendChild(plugin_style);
}

if (PlaceholderData.custom_css != "") {
    debug("Applied the plugin's CSS (fixes some visual bugs)");
    PlaceholderPlugin.add_default_style();
} else {
    console.warn("Since fix_style is not enabled, you may experience some visaul bugs");
}

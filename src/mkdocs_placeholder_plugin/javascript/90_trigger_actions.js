PlaceholderPlugin.init = () => {
    PlaceholderPlugin.initialize_undefined_placeholders();

    PlaceholderPlugin.prepare_variable_input_fields();
    
    const replace_root = document.querySelector("html");
    const used_placeholders = PlaceholderPlugin.replace_placeholders_in_subtree(replace_root);
    debug("Used placeholder list:", used_placeholders);

    PlaceholderPlugin.initialize_auto_tables(used_placeholders);
}

// Then do the placeholder replacing at the user-specified time
if (PlaceholderData.delay_millis < 0) {
    // For values smaller than 0, immediately do the replacements
    PlaceholderPlugin.init();
} else if (PlaceholderData.delay_millis == 0) {
    // Replace placeholders as soon as the page finished loading
    window.addEventListener("load", PlaceholderPlugin.init);
} else {
    // Wait the amount of millis specified by the user
    window.addEventListener("load", () => {
        setTimeout(PlaceholderPlugin.init, PlaceholderData.delay_millis);
    });
}

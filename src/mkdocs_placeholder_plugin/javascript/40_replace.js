// Replace a specific placeholder and return the estimated number of occurences (underestimated, may actually be higher)
PlaceholderPlugin.replace_text_in_page = (root_element, search_regex, replacement_value) => {
    const walker = document.createTreeWalker(root_element, NodeFilter.SHOW_TEXT);
    let node;
    let count = 0;
    while (node = walker.nextNode()) {
        replaced_str = node.nodeValue.replaceAll(search_regex, replacement_value);
        if (node.nodeValue != replaced_str) {
            node.nodeValue = replaced_str;
            count++; // Of course, it might have been replaced multiple times by replaceAll. But this is just for debugging
            // and performing an accurate count would impact the performace.
        }
    }
    return count;
};

// Replace all placeholders in the given order and return which placeholders actually were actually found in the page
PlaceholderPlugin.replace_placeholders_in_subtree = (root_element) => {
    used_placeholders = [];
    for (let placeholder of PlaceholderData.names) {
        const search_regex = RegExp("x" + placeholder + "x", "g");
        let replace_value = localStorage.getItem(placeholder);
        if (replace_value == null) {
            console.warn(`Undefined value for placeholder '${placeholder}'`);
            replace_value = "<BUG:no_value_for_placeholder>"
        }
        count = PlaceholderPlugin.replace_text_in_page(root_element, search_regex, replace_value);
        if (count != 0) {
            debug(`Replaced ${placeholder} at least ${count} time(s)`);
            // store all used placeholder names
            used_placeholders.push(placeholder);
        }
    }
    return used_placeholders;
};


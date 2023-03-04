PlaceholderPlugin.escapeHTML = (text) => {
    const element = document.createElement("div");
    element.appendChild(document.createTextNode(text));
    return element.innerHTML;
}

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

PlaceholderPlugin.replace_everywhere_in_page = (root_element, search_regex, replacement_value) => {
    // User supplied input, HTML escape it before we inject it in the page
    replacement_value = PlaceholderPlugin.escapeHTML(replacement_value);

    const new_value = root_element.innerHTML.replaceAll(search_regex, replacement_value);
    if (new_value != root_element.innerHTML) {
        root_element.innerHTML = new_value;
        return 1;
    } else {
        return 0;
    }
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
        const replace_everywhere = PlaceholderData.common_map[placeholder].replace_everywhere;
        if (replace_everywhere) {
            debug(`Warning: replace_everywhere set for ${placeholder}`)
        }
        const replace_fn = replace_everywhere? PlaceholderPlugin.replace_everywhere_in_page : PlaceholderPlugin.replace_text_in_page;
        count = replace_fn(root_element, search_regex, replace_value);
        if (count != 0) {
            debug(`Replaced ${placeholder} at least ${count} time(s)`);
            // store all used placeholder names
            used_placeholders.push(placeholder);
        }
    }
    return used_placeholders;
};


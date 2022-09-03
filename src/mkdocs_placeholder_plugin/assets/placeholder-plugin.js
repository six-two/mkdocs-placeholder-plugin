// Do not expose our methods to the outside (prevent accidentially shadowing stuff)
(function() {
    PLACEHOLDER_DEFAULTS = __MKDOCS_PLACEHOLDER_PLUGIN_JSON__;
    REPLACE_TRIGGER_DELAY_MILLIS = __MKDOCS_REPLACE_TRIGGER_DELAY_MILLIS__;

    const replace_text_in_page = (root_element, search_regex, replacement_value) => {
        const walker = document.createTreeWalker(root_element, NodeFilter.SHOW_TEXT);
        let node;
        while (node = walker.nextNode()) {
            node.nodeValue = node.nodeValue.replaceAll(search_regex, replacement_value);
        }
    };

    const replace_placeholders_in_subtree = (root_element) => {
        for (let placeholder in PLACEHOLDER_DEFAULTS) {
            let replace_value = localStorage.getItem(placeholder);
            if (!replace_value) {
                replace_value = PLACEHOLDER_DEFAULTS[placeholder];
                localStorage.setItem(placeholder, replace_value);
            }
            // We need to chose a format, that does not get broken up by the syntax highlighting in code snippets.
            // I would hav liked something like @{PLACEHOLDER}@, but __PLACEHOLDER__ would probably be safest
            // Turns out __PLACEHOLDER__ is the markdown syntax for bold. Thus it works fine in code listings, but not in normal text.
            // Ok, let's try xPLACEHOLDERx. This uses just normal letters and has a beginning and end marker (assuming PLACEHOLdER is always uppercase).
            const search_regex = RegExp("x" + placeholder + "x", "g");
            replace_text_in_page(root_element, search_regex, replace_value);
        }
    };

    const replace_placeholders = () => {
        const replace_root = document.querySelector("html");
        replace_placeholders_in_subtree(replace_root);
    };

    const prepare_variable_input_fields = () => {
        const input_list = document.querySelectorAll("input[data-input-for]");
        console.log(`Found ${input_list.length} input fields`);
        for (let input of input_list) {
            input.classList.add("input-for-variable");
            const variable_name = input.getAttribute("data-input-for");
            input.value = localStorage.getItem(variable_name) || variable_name + " is undefined";
            input.addEventListener("change", () => {
                localStorage.setItem(variable_name, input.value);
            });
        }
    };

    // Set up the input fields for the placeholder fields
    window.addEventListener("load", prepare_variable_input_fields);

    // Then do the placeholder replacing at the user-specified time
    if (REPLACE_TRIGGER_DELAY_MILLIS < 0) {
        // For values smaller than 0, immediately do the replacements
        replace_placeholders();
    } else if (REPLACE_TRIGGER_DELAY_MILLIS == 0) {
        // Replace placeholders as soon as the page finished loading
        window.addEventListener("load", replace_placeholders);
    } else {
        // Wait the amount of millis specified by the user
        window.addEventListener("load", () => {
            setTimeout(replace_placeholders, REPLACE_TRIGGER_DELAY_MILLIS);
        });
    }
}());
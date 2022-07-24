// Do not expose our methods to the outside (prevent accidentially shadowing stuff)
(function() {
    const replace_text_in_page = (search_regex, replacement_value) => {
        const html = document.querySelector('html');
        const walker = document.createTreeWalker(html, NodeFilter.SHOW_TEXT);
        let node;
        while (node = walker.nextNode()) {
            node.nodeValue = node.nodeValue.replaceAll(search_regex, replacement_value);
        }
    };

    // Set up the input fields for the placeholder fields
    window.addEventListener("load", () => {
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
    });

    PLACEHOLDER_DEFAULTS = __MKDOCS_PLACEHOLDER_PLUGIN_JSON__;

    // After the page is loaded, replace the placeholders.
    // This will also give other script time to change the placeholder values (if desired)
    window.addEventListener("load", () => {
        console.log("Replacing placeholder variables")
        for (let placeholder in PLACEHOLDER_DEFAULTS) {
            let replace_value = localStorage.getItem(placeholder);
            if (!replace_value){
                replace_value = PLACEHOLDER_DEFAULTS[placeholder];
                localStorage.setItem(placeholder, replace_value);
            }
            // We need to chose a format, that does not get broken up by the syntax highlighting in code snippets.
            // I would hav liked something like @{PLACEHOLDER}@, but __PLACEHOLDER__ would probably be safest
            // Turns out __PLACEHOLDER__ is the markdown syntax for bold. Thus it works fine in code listings, but not in normal text.
            // Ok, let's try xPLACEHOLDERx. This uses just normal letters and has a beginning and end marker (assuming PLACEHOLdER is always uppercase).
            const search_regex = RegExp("x"+placeholder+"x", "g");
            replace_text_in_page(search_regex, replace_value);
        }
    });
}());


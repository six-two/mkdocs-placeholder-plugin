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

    const initialize_undefined_placeholders = () => {
        init_count = 0;
        for (let placeholder in PLACEHOLDER_DEFAULTS) {
            if (!localStorage.getItem(placeholder)) {
                localStorage.setItem(placeholder, PLACEHOLDER_DEFAULTS[placeholder]);
                init_count++;
            }
        }
        if (init_count > 0) {
            console.log(`Initialized ${init_count} placeholder(s) with default values`);
        }
    }

    const replace_placeholders_in_subtree = (root_element) => {
        for (let placeholder in PLACEHOLDER_DEFAULTS) {
            const search_regex = RegExp("x" + placeholder + "x", "g");
            const replace_value = localStorage.getItem(placeholder) || "BUG: Value missing";
            replace_text_in_page(root_element, search_regex, replace_value);
        }
    };
    
    const prepare_variable_input_fields = () => {
        const input_list = document.querySelectorAll("input[data-input-for]");
        console.log(`Found ${input_list.length} input field(s)`);
        for (let input of input_list) {
            input.classList.add("input-for-variable");
            const variable_name = input.getAttribute("data-input-for");
            input.value = localStorage.getItem(variable_name) || variable_name + " is undefined";
            input.addEventListener("change", () => {
                localStorage.setItem(variable_name, input.value);
            });
        }
    };
    
    const init = () => {
        initialize_undefined_placeholders();

        prepare_variable_input_fields();
        
        const replace_root = document.querySelector("html");
        replace_placeholders_in_subtree(replace_root);
    }

    
    // Then do the placeholder replacing at the user-specified time
    if (REPLACE_TRIGGER_DELAY_MILLIS < 0) {
        // For values smaller than 0, immediately do the replacements
        init();
    } else if (REPLACE_TRIGGER_DELAY_MILLIS == 0) {
        // Replace placeholders as soon as the page finished loading
        window.addEventListener("load", init);
    } else {
        // Wait the amount of millis specified by the user
        window.addEventListener("load", () => {
            setTimeout(init, REPLACE_TRIGGER_DELAY_MILLIS);
        });
    }
}());
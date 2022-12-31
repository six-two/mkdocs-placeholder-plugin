// Do not expose our methods to the outside (prevent accidentially shadowing stuff)
(function() {
    DATA_FROM_MKDOCS_PLUGIN = __MKDOCS_PLACEHOLDER_PLUGIN_JSON__;
    REPLACE_TRIGGER_DELAY_MILLIS = __MKDOCS_REPLACE_TRIGGER_DELAY_MILLIS__;

    // name:str -> default_value:str
    TEXTBOX_DATA = DATA_FROM_MKDOCS_PLUGIN["textbox"];
    // name:str -> { "checked" -> value:str, "unchecked" -> value:str, "default_value" -> checked_by_default:bool }
    CHECKBOX_DATA = DATA_FROM_MKDOCS_PLUGIN["checkbox"];
    // name:str -> { "default_index" -> default:int, "options" -> list of [display_name:str, actual_value:str] }
    DROPDOWN_DATA = DATA_FROM_MKDOCS_PLUGIN["dropdown"];
    // list of name:str
    PLACEHOLDER_NAMES = DATA_FROM_MKDOCS_PLUGIN["placeholder_names"];

    const replace_text_in_page = (root_element, search_regex, replacement_value) => {
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

    const store_checkbox_state = (placeholder_name, new_is_checked) => {
        data = CHECKBOX_DATA[placeholder_name];
        value = new_is_checked ? "checked" : "unchecked";

        // Store the actual placeholder value
        localStorage.setItem(placeholder_name, data[value]);
        // Store whether it is checked in an extra variable
        localStorage.setItem(`${placeholder_name}__STATE__`, value);
    }

    const load_checkbox_state = (placeholder_name) => {
        stored_state = localStorage.getItem(`${placeholder_name}__STATE__`)
        
        if (stored_state == null) {
            // no state is stored, so we check the default value
            data = CHECKBOX_DATA[placeholder_name];
            return data["default_value"]
        } else {
            return stored_state == "checked"
        }
    }

    const store_dropdown_state = (placeholder_name, new_index) => {
        data = DROPDOWN_DATA[placeholder_name];

        // Store the actual placeholder value
        value = data["options"][new_index][1] // 1: value, 0 would be display name
        localStorage.setItem(placeholder_name, value);
        // Store whether it is checked in an extra variable
        localStorage.setItem(`${placeholder_name}__STATE__`, "" + new_index);
    }

    const load_dropdown_state = (placeholder_name) => {
        stored_state = localStorage.getItem(`${placeholder_name}__STATE__`)
        
        data = DROPDOWN_DATA[placeholder_name];
        if (stored_state == null) {
            // no state is stored, so we check the default value
            return data["default_index"]
        } else {
            value = parseInt(stored_state, 10)
            return Math.max(0, Math.min(value, data["options"].length))
        }
    }

    const initialize_undefined_placeholders = () => {
        init_count = 0;
        for (let placeholder in TEXTBOX_DATA) {
            if (!localStorage.getItem(placeholder)) {
                const value = TEXTBOX_DATA[placeholder]["value"];
                localStorage.setItem(placeholder, value);
                init_count++;
            }
        }
        for (let placeholder in CHECKBOX_DATA) {
            if (!localStorage.getItem(placeholder)) {
                init_count++;
            }
            // we load and store EVERY item, in case the values for checked and uncheked states have changed since the last visit to the website
            value = load_checkbox_state(placeholder);
            store_checkbox_state(placeholder, value);
        }
        for (let placeholder in DROPDOWN_DATA) {
            if (!localStorage.getItem(placeholder)) {
                init_count++;
            }
            // we load and store EVERY item, in case the values for checked and uncheked states have changed since the last visit to the website
            // Since we store the index, if the order changes, this will not be handled well
            value = load_dropdown_state(placeholder);
            store_dropdown_state(placeholder, value);
        }
        if (init_count > 0) {
            console.log(`Initialized ${init_count} placeholder(s) with default values`);
        }
    }

    const replace_placeholders_in_subtree = (root_element) => {
        for (let placeholder of PLACEHOLDER_NAMES) {
            const search_regex = RegExp("x" + placeholder + "x", "g");
            const replace_value = localStorage.getItem(placeholder) || "BUG: Value missing";
            count = replace_text_in_page(root_element, search_regex, replace_value);
            if (count != 0) {
                console.debug(`Replaced ${placeholder} at least ${count} time(s)`);
            }
        }
    };
    
    // For normal text fields
    const prepare_textbox_field = (placeholder_name, input_element) => {
        // Restore the stored state
        input_element.value = localStorage.getItem(placeholder_name) || placeholder_name + " is undefined";

        data = TEXTBOX_DATA[placeholder_name];
        if (data["read_only"]) {
            // disable the checkbox
            input_element.disabled = "1";
            input_element.style.cursor = "not-allowed";
        } else {
            // Listen for state changes
            input_element.addEventListener("change", () => {
                localStorage.setItem(placeholder_name, input_element.value);
            });
        }
    };

    // For checkbox fields
    const prepare_checkbox_field = (placeholder_name, input_element) => {
        // Restore the stored state
        data = CHECKBOX_DATA[placeholder_name];
        last_state = load_checkbox_state(placeholder_name);
        input_element.type = "checkbox";
        input_element.checked = last_state;
        if (data["read_only"]) {
            // disable the checkbox
            input_element.disabled = "1";
        } else {
            // Listen for state changes
            input_element.addEventListener("change", () => {
                store_checkbox_state(placeholder_name, input_element.checked);
            });
        }
    };

    // For dropdown fields
    const prepare_dropdown_field = (placeholder_name, input_element) => {
        // Restore the stored state
        const new_node = document.createElement("select");
        data = DROPDOWN_DATA[placeholder_name];
        option_list = data["options"];

        for (var i = 0; i < option_list.length; i++) {
            const option = document.createElement("option");
            option.text = option_list[i][0];
            new_node.appendChild(option);
        }
        // Replace input element entirely with the dropdown menu
        input_element.parentNode.replaceChild(new_node, input_element);

        // Select the stored option
        selected_index = load_dropdown_state(placeholder_name);
        new_node.selectedIndex = selected_index;

        if (data["read_only"]) {
            // disable the dropdown
            new_node.disabled = "1";
        } else{
            // Add an event listener
            new_node.addEventListener("change", () => {
                console.log("change", new_node.selectedIndex);
                store_dropdown_state(placeholder_name, new_node.selectedIndex);
            })
        }
    };

    const prepare_variable_input_fields = () => {
        const input_list = document.querySelectorAll("input[data-input-for]");
        checkbox_count = 0;
        dropdown_count = 0;
        textbox_count = 0;
        for (let input of input_list) {
            input.classList.add("input-for-variable");
            const placeholder_name = input.getAttribute("data-input-for");

            if (CHECKBOX_DATA[placeholder_name]) {
                // The placeholder is a checkbox
                prepare_checkbox_field(placeholder_name, input);
                checkbox_count++;
            } else if (DROPDOWN_DATA[placeholder_name]) {
                // The placeholder is a dropdown menu
                prepare_dropdown_field(placeholder_name, input);
                dropdown_count++;
            } else if (TEXTBOX_DATA[placeholder_name]) {
                // The placeholder is a textbox
                prepare_textbox_field(placeholder_name, input);
                textbox_count++;
            }
        }
        checkbox_count > 0 && console.log(`Found ${checkbox_count} checkbox field(s)`);
        dropdown_count > 0 && console.log(`Found ${dropdown_count} dropdown field(s)`);
        textbox_count > 0 && console.log(`Found ${textbox_count} textbox field(s)`);
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
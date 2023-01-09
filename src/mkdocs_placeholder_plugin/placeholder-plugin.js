// Exposed functionality will be stored in this
const MkdocsPlaceholderPlugin = (function() {
    // Do not expose our methods to the outside (prevent accidentially shadowing stuff) by default
    DATA_FROM_MKDOCS_PLUGIN = __MKDOCS_PLACEHOLDER_PLUGIN_JSON__;
    // Set up or disable logging as early as possible
    let log, debug;
    if (DATA_FROM_MKDOCS_PLUGIN["debug"]) {
        // Write debugging messages to console
        debug = console.debug;
        log = console.log;
    } else {
        // If debugging is disabled, make the functions do nothing
        debug = () => {};
        log = () => {};
    }

    debug("Data from plugin:");
    for (key in DATA_FROM_MKDOCS_PLUGIN) {
        debug(`  - ${key}:`, DATA_FROM_MKDOCS_PLUGIN[key]);
    }

    // int
    REPLACE_TRIGGER_DELAY_MILLIS = DATA_FROM_MKDOCS_PLUGIN["delay_millis"];
    // bool
    RELOAD_ON_CHANGE = DATA_FROM_MKDOCS_PLUGIN["reload"];
    // name:str -> { "value" -> default_value:str, "read_only" -> bool }
    TEXTBOX_DATA = DATA_FROM_MKDOCS_PLUGIN["textbox"];
    // name:str -> { "checked" -> value:str, "unchecked" -> value:str, "default_value" -> checked_by_default:bool, "read_only" -> bool }
    CHECKBOX_DATA = DATA_FROM_MKDOCS_PLUGIN["checkbox"];
    // name:str -> { "default_index" -> default:int, "options" -> list of [display_name:str, actual_value:str], "read_only" -> bool }
    DROPDOWN_DATA = DATA_FROM_MKDOCS_PLUGIN["dropdown"];
    // list of name:str
    PLACEHOLDER_NAMES = DATA_FROM_MKDOCS_PLUGIN["placeholder_names"];


    // Constants
    TABLE_CELL_HEADINGS = {
        "name": "Name",
        "description": "Description",
        "value": "Value",
        "input": "Input element",
    }


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

    const on_placeholder_change = () => {
        if (RELOAD_ON_CHANGE){
            debug("Reloading page to update placeholder values");
            window.location.reload();
        }
    }

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
            log(`Initialized ${init_count} placeholder(s) with default values`);
        }
    }

    const replace_placeholders_in_subtree = (root_element) => {
        used_placeholders = [];
        for (let placeholder of PLACEHOLDER_NAMES) {
            const search_regex = RegExp("x" + placeholder + "x", "g");
            let replace_value = localStorage.getItem(placeholder);
            if (replace_value == null) {
                console.warn(`Undefined value for placeholder '${placeholder}'`);
                replace_value = "<BUG:no_value_for_placeholder>"
            }
            count = replace_text_in_page(root_element, search_regex, replace_value);
            if (count != 0) {
                debug(`Replaced ${placeholder} at least ${count} time(s)`);
                // store all used placeholder names
                used_placeholders.push(placeholder);
            }
        }
        return used_placeholders;
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
            input_element.addEventListener("keypress", e => {
                if (e.key === "Enter") {
                    debug("Textbox change confirmed with Enter key for ", placeholder_name, "- new value:", input_element.checked);
                    on_placeholder_change();
                }
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
                debug("Checkbox change", placeholder_name, "- new value:", input_element.checked);
                store_checkbox_state(placeholder_name, input_element.checked);
                on_placeholder_change();
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
                debug("Dropdown change", placeholder_name, "- new index:", new_node.selectedIndex);
                store_dropdown_state(placeholder_name, new_node.selectedIndex);
                on_placeholder_change();
            })
        }
    };

    const prepare_variable_input_fields = () => {
        const input_list = document.querySelectorAll("input[data-input-for]");
        checkbox_count = 0;
        dropdown_count = 0;
        textbox_count = 0;
        for (let input of input_list) {
            const placeholder_name = input.getAttribute("data-input-for");
            prepare_input_field_for_placeholder(placeholder_name, input);
        }
        checkbox_count > 0 && log(`Found ${checkbox_count} checkbox field(s)`);
        dropdown_count > 0 && log(`Found ${dropdown_count} dropdown field(s)`);
        textbox_count > 0 && log(`Found ${textbox_count} textbox field(s)`);
    };

    const prepare_input_field_for_placeholder = (placeholder_name, input) => {
        input.classList.add("input-for-variable");

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
        } else {
            console.warn(`Unknown placeholder referenced in input element: '${placeholder_name}'`)
        }
    }

    const generate_automatic_placeholder_table = (element, columns, used_placeholders) => {
        if (used_placeholders.length == 0) {
            // Do not create an empty table
            return;
        }

        debug("Creating automatic input table at", element, `with columns ${columns}`);
        element.innerHTML = ""; // remove all children
        table = document.createElement("table");
        table_head = document.createElement("thead");
        table_head_row = document.createElement("tr");
        table_body = document.createElement("tbody");
        //
        element.appendChild(table);
        table.appendChild(table_head);
        table.appendChild(table_body);
        table_head.appendChild(table_head_row);

        for (column of columns) {
            table_cell = document.createElement("th");
            table_cell.appendChild(document.createTextNode(TABLE_CELL_HEADINGS[column]))
            table_head_row.appendChild(table_cell);
        }

        for (placeholder_name of used_placeholders) {
            row = document.createElement("tr");
            for (column of columns) {
                cell = document.createElement("td");
                row.appendChild(cell);

                if (column == "name") {
                    cell.appendChild(document.createTextNode(placeholder_name));
                } else if (column == "description") {
                    // TODO: needs plugin support
                    cell.appendChild(document.createTextNode("TODO"));
                } else if (column == "value") {
                    cell.appendChild(document.createTextNode(`x${placeholder_name}x`));
                    // @TODO: recursive raplacing ov values
                } else if (column == "input") {
                    input = document.createElement("input");
                    cell.appendChild(input);
                    prepare_input_field_for_placeholder(placeholder_name, input);
                } else {
                    console.error(`Unknown column name: ${column}`);
                }
            }
            table_body.appendChild(row);
        }
        replace_placeholders_in_subtree(element);
    }

    const initialize_auto_tables = (used_placeholders) => {
        const element_list = document.querySelectorAll("div.auto-input-table");
        for (let element of element_list) {
            const columns_str = element.getAttribute("data-columns") || "name,input";
            const columns = columns_str.includes(",")? columns_str.split(",") : [columns_str];
            debug("Auto table", element, used_placeholders, columns);
            generate_automatic_placeholder_table(element, columns, used_placeholders);
        }
    };
    
    const init = () => {
        initialize_undefined_placeholders();

        prepare_variable_input_fields();
        
        const replace_root = document.querySelector("html");
        const used_placeholders = replace_placeholders_in_subtree(replace_root);
        debug("Used placeholder list:", used_placeholders);

        initialize_auto_tables(used_placeholders);
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

    return {
        "config": DATA_FROM_MKDOCS_PLUGIN,
    }
}());
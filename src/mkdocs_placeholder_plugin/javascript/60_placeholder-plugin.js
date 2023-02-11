// @TODO: further split up and make functions globally available
(function() {
    // Constants
    TABLE_CELL_HEADINGS = {
        "name": "Name",
        "description": "Description",
        "value": "Value",
        "input": "Input element",
        "description-or-name": "Description / name",
    }

    const on_placeholder_change = () => {
        if (PlaceholderData.reload){
            debug("Reloading page to update placeholder values");
            window.location.reload();
        }
    }

    
    // For normal text fields
    const prepare_textbox_field = (placeholder_name, input_element) => {
        // Restore the stored state
        input_element.value = localStorage.getItem(placeholder_name) || placeholder_name + " is undefined";

        data = PlaceholderData.textbox_map[placeholder_name];
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
        data = PlaceholderData.checkbox_map[placeholder_name];
        last_state = PlaceholderPlugin.load_checkbox_state(placeholder_name);
        input_element.type = "checkbox";
        input_element.checked = last_state;
        if (data["read_only"]) {
            // disable the checkbox
            input_element.disabled = "1";
        } else {
            // Listen for state changes
            input_element.addEventListener("change", () => {
                debug("Checkbox change", placeholder_name, "- new value:", input_element.checked);
                PlaceholderPlugin.store_checkbox_state(placeholder_name, input_element.checked);
                on_placeholder_change();
            });
        }
    };

    // For dropdown fields
    const prepare_dropdown_field = (placeholder_name, input_element) => {
        // Restore the stored state
        const new_node = document.createElement("select");
        new_node.classList.add("placeholder-dropdown"); 
        data = PlaceholderData.dropdown_map[placeholder_name];
        option_list = data["options"];

        for (var i = 0; i < option_list.length; i++) {
            const option = document.createElement("option");
            option.text = option_list[i][0];
            new_node.appendChild(option);
        }
        // Replace input element entirely with the dropdown menu
        input_element.parentNode.replaceChild(new_node, input_element);

        // Select the stored option
        selected_index = PlaceholderPlugin.load_dropdown_state(placeholder_name);
        new_node.selectedIndex = selected_index;

        if (data["read_only"]) {
            // disable the dropdown
            new_node.disabled = "1";
        } else{
            // Add an event listener
            new_node.addEventListener("change", () => {
                debug("Dropdown change", placeholder_name, "- new index:", new_node.selectedIndex);
                PlaceholderPlugin.store_dropdown_state(placeholder_name, new_node.selectedIndex);
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

        if (PlaceholderData.checkbox_map[placeholder_name]) {
            // The placeholder is a checkbox
            prepare_checkbox_field(placeholder_name, input);
            checkbox_count++;
        } else if (PlaceholderData.dropdown_map[placeholder_name]) {
            // The placeholder is a dropdown menu
            prepare_dropdown_field(placeholder_name, input);
            dropdown_count++;
        } else if (PlaceholderData.textbox_map[placeholder_name]) {
            // The placeholder is a textbox
            prepare_textbox_field(placeholder_name, input);
            textbox_count++;
        } else {
            console.warn(`Unknown placeholder referenced in input element: '${placeholder_name}'`)
        }
    }

    const appendTextNode = (element, text) => {
        element.appendChild(document.createTextNode(text));
    }

    const createChildElement = (parent, tag_name) => {
        child = document.createElement(tag_name);
        parent.appendChild(child);
        return child;
    }

    const generate_automatic_placeholder_table = (element, columns, used_placeholders) => {
        if (used_placeholders.length == 0) {
            // Do not create an empty table
            return;
        }

        info("Creating automatic input table at", element, "with columns", columns);
        // element.innerHTML = ""; // remove all children
        table = createChildElement(element, "table");
        table_head = createChildElement(table, "thead");
        table_head_row = createChildElement(table_head, "tr");
        table_body = createChildElement(table, "tbody");

        for (column of columns) {
            table_cell = createChildElement(table_head_row, "th");
            appendTextNode(table_cell, TABLE_CELL_HEADINGS[column]);
        }

        for (placeholder_name of used_placeholders) {
            row = document.createElement("tr");
            for (column of columns) {
                cell = document.createElement("td");
                row.appendChild(cell);

                if (column == "name") {
                    appendTextNode(cell, placeholder_name);
                } else if (column == "description") {
                    appendTextNode(cell, PlaceholderData.description_map[placeholder_name]);
                } else if (column == "value") {
                    appendTextNode(cell, `x${placeholder_name}x`);
                } else if (column == "input") {
                    input = createChildElement(cell, "input");
                    prepare_input_field_for_placeholder(placeholder_name, input);
                } else if (column == "description-or-name") {
                    const text = PlaceholderData.description_map[placeholder_name] || placeholder_name;
                    appendTextNode(cell, text);
                } else {
                    console.error(`Unknown column name: ${column}`);
                }
            }
            table_body.appendChild(row);
        }
        PlaceholderPlugin.replace_placeholders_in_subtree(element);
    }

    const initialize_auto_tables = (used_placeholders) => {
        const element_list = document.querySelectorAll("div.auto-input-table");
        for (let element of element_list) {
            const columns_str = element.getAttribute("data-columns") || "name,input";
            const columns = columns_str.includes(",")? columns_str.split(",") : [columns_str];
            generate_automatic_placeholder_table(element, columns, used_placeholders);
        }
    };
    
    PlaceholderPlugin.init = () => {
        PlaceholderPlugin.initialize_undefined_placeholders();

        prepare_variable_input_fields();
        
        const replace_root = document.querySelector("html");
        const used_placeholders = PlaceholderPlugin.replace_placeholders_in_subtree(replace_root);
        debug("Used placeholder list:", used_placeholders);

        initialize_auto_tables(used_placeholders);
    }
}());

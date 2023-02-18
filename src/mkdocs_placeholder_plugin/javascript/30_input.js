PlaceholderPlugin.on_placeholder_change = () => {
    if (PlaceholderData.reload){
        debug("Reloading page to update placeholder values");
        PlaceholderPlugin.reload_page();
    }
}

// For normal text fields
PlaceholderPlugin.prepare_textbox_field = (placeholder_name, input_element) => {
    // Restore the stored state
    input_element.value = localStorage.getItem(placeholder_name) || placeholder_name + " is undefined";

    let data = PlaceholderData.textbox_map[placeholder_name];
    if (data["read_only"]) {
        // disable the checkbox
        input_element.disabled = "1";
        input_element.style.cursor = "not-allowed";
    } else {
        // Check if initial value is valid
        PlaceholderPlugin.validate_input_field(input_element, placeholder_name, false);

        // Listen for state changes
        input_element.addEventListener("input", () => {
            PlaceholderPlugin.validate_input_field(input_element, placeholder_name, false);
        });
        input_element.addEventListener("keypress", e => {
            if (e.key === "Enter") {
                debug("Textbox change confirmed with Enter key for ", placeholder_name, "- new value:", input_element.checked);
                // PlaceholderPlugin.store_textbox_state(placeholder_name, input_element.value);
                PlaceholderPlugin.validate_input_field(input_element, placeholder_name, true);
            }
        });
        // Return an action to perform when the apply button is clicked
        return () => PlaceholderPlugin.store_textbox_state(placeholder_name, input_element.value);
    }
};

// For checkbox fields
PlaceholderPlugin.prepare_checkbox_field = (placeholder_name, input_element) => {
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
            PlaceholderPlugin.on_placeholder_change();
        });
    }
};

// For dropdown fields
PlaceholderPlugin.prepare_dropdown_field = (placeholder_name, input_element) => {
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
    } else {
        // Add an event listener
        new_node.addEventListener("change", () => {
            debug("Dropdown change", placeholder_name, "- new index:", new_node.selectedIndex);
            PlaceholderPlugin.store_dropdown_state(placeholder_name, new_node.selectedIndex);
            PlaceholderPlugin.on_placeholder_change();
        });
    }
};

// Prepare a placeholder input field. Returns the method to apply the current value (that will be executed when/if the "Apply new values" button is clicked)
PlaceholderPlugin.prepare_input_field_for_placeholder = (placeholder_name, input) => {
    input.classList.add("input-for-variable");

    if (PlaceholderData.checkbox_map[placeholder_name]) {
        // The placeholder is a checkbox
        checkbox_count++;
        return PlaceholderPlugin.prepare_checkbox_field(placeholder_name, input);
    } else if (PlaceholderData.dropdown_map[placeholder_name]) {
        // The placeholder is a dropdown menu
        dropdown_count++;
        return PlaceholderPlugin.prepare_dropdown_field(placeholder_name, input);
    } else if (PlaceholderData.textbox_map[placeholder_name]) {
        // The placeholder is a textbox
        textbox_count++;
        return PlaceholderPlugin.prepare_textbox_field(placeholder_name, input);
    } else {
        console.warn(`Unknown placeholder referenced in input element: '${placeholder_name}'`);
    }
}

PlaceholderPlugin.prepare_variable_input_fields = () => {
    const input_list = document.querySelectorAll("input[data-input-for]");
    checkbox_count = 0;
    dropdown_count = 0;
    textbox_count = 0;
    for (let input of input_list) {
        const placeholder_name = input.getAttribute("data-input-for");
        PlaceholderPlugin.prepare_input_field_for_placeholder(placeholder_name, input);
    }
    checkbox_count > 0 && log(`Found ${checkbox_count} checkbox field(s)`);
    dropdown_count > 0 && log(`Found ${dropdown_count} dropdown field(s)`);
    textbox_count > 0 && log(`Found ${textbox_count} textbox field(s)`);
};

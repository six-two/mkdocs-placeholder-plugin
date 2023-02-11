PlaceholderPlugin.store_checkbox_state = (placeholder_name, new_is_checked) => {
    data = PlaceholderData.checkbox_map[placeholder_name];
    value = new_is_checked ? "checked" : "unchecked";

    // Store the actual placeholder value
    localStorage.setItem(placeholder_name, data[value]);
    // Store whether it is checked in an extra variable
    localStorage.setItem(`${placeholder_name}__STATE__`, value);
}

PlaceholderPlugin.load_checkbox_state = (placeholder_name) => {
    stored_state = localStorage.getItem(`${placeholder_name}__STATE__`)
    
    if (stored_state == null) {
        // no state is stored, so we check the default value
        data = PlaceholderData.checkbox_map[placeholder_name];
        return data["default_value"]
    } else {
        return stored_state == "checked"
    }
}

PlaceholderPlugin.store_dropdown_state = (placeholder_name, new_index) => {
    data = PlaceholderData.dropdown_map[placeholder_name];

    const new_value_data = data["options"][new_index];
    if (new_value_data){
        // Store the actual placeholder value//@TODO dangerous
        value = new_value_data[1] // 1: value, 0 would be display name
        localStorage.setItem(placeholder_name, value);
        // Store whether it is checked in an extra variable
        localStorage.setItem(`${placeholder_name}__STATE__`, "" + new_index);
    } else {
        console.warn(`Tried to store state '${new_index}' for placeholder ${placeholder_name}, but the only valid names are:`, Object.keys(value["options"]))
    }
}

PlaceholderPlugin.load_dropdown_state = (placeholder_name) => {
    stored_state = localStorage.getItem(`${placeholder_name}__STATE__`)
    
    data = PlaceholderData.dropdown_map[placeholder_name];
    if (stored_state == null) {
        // no state is stored, so we check the default value
        return data["default_index"]
    } else {
        value = parseInt(stored_state, 10)
        return Math.max(0, Math.min(value, data["options"].length))
    }
}

PlaceholderPlugin.initialize_undefined_placeholders = () => {
    init_count = 0;
    for (let placeholder in PlaceholderData.textbox_map) {
        if (!localStorage.getItem(placeholder)) {
            const value = PlaceholderData.textbox_map[placeholder]["value"];
            localStorage.setItem(placeholder, value);
            init_count++;
        }
    }
    for (let placeholder in PlaceholderData.checkbox_map) {
        if (!localStorage.getItem(placeholder)) {
            init_count++;
        }
        // we load and store EVERY item, in case the values for checked and uncheked states have changed since the last visit to the website
        value = PlaceholderPlugin.load_checkbox_state(placeholder);
        PlaceholderPlugin.store_checkbox_state(placeholder, value);
    }
    for (let placeholder in PlaceholderData.dropdown_map) {
        if (!localStorage.getItem(placeholder)) {
            init_count++;
        }
        // we load and store EVERY item, in case the values for checked and uncheked states have changed since the last visit to the website
        // Since we store the index, if the order changes, this will not be handled well
        value = PlaceholderPlugin.load_dropdown_state(placeholder);
        PlaceholderPlugin.store_dropdown_state(placeholder, value);
    }
    if (init_count > 0) {
        log(`Initialized ${init_count} placeholder(s) with default values`);
    }
}

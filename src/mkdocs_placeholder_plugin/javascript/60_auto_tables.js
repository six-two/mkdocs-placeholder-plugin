PlaceholderPlugin.TABLE_CELL_HEADINGS = {
    "name": "Name",
    "description": "Description",
    "value": "Value",
    "input": "Input element",
    "description-or-name": "Description / name",
}

PlaceholderPlugin.generate_automatic_placeholder_table = (element, columns, used_placeholders) => {
    if (used_placeholders.length == 0) {
        // Do not create an empty table
        return;
    }

    // Helper functions to simplify the following code
    const appendTextNode = (element, text) => {
        element.appendChild(document.createTextNode(text));
    }

    const createChildElement = (parent, tag_name) => {
        const child = document.createElement(tag_name);
        parent.appendChild(child);
        return child;
    }

    info("Creating automatic input table at", element, "with columns", columns);
    // element.innerHTML = ""; // remove all children
    const table = createChildElement(element, "table");
    const table_head = createChildElement(table, "thead");
    const table_head_row = createChildElement(table_head, "tr");
    const table_body = createChildElement(table, "tbody");

    for (const column of columns) {
        const table_cell = createChildElement(table_head_row, "th");
        appendTextNode(table_cell, PlaceholderPlugin.TABLE_CELL_HEADINGS[column]);
    }

    const apply_actions = [];
    for (placeholder_name of used_placeholders) {
        if (PlaceholderData.auto_table_hide_read_only && 
                    PlaceholderData.common_map[placeholder_name].read_only) {
            debug(`auto_table: Skipping ${placeholder_name} because it is read-only`)
            continue
        }
        const row = createChildElement(table_body, "tr");
        for (const column of columns) {
            const cell = createChildElement(row, "td");

            if (column == "name") {
                appendTextNode(cell, placeholder_name);
            } else if (column == "description") {
                appendTextNode(cell, PlaceholderData.common_map[placeholder_name].description);
            } else if (column == "value") {
                appendTextNode(cell, `x${placeholder_name}x`);
            } else if (column == "input") {
                const input = createChildElement(cell, "input");
                const action = PlaceholderPlugin.prepare_input_field_for_placeholder(placeholder_name, input);
                if (typeof(action) == "function") {
                    apply_actions.push(action);
                }
            } else if (column == "description-or-name") {
                const text = PlaceholderData.common_map[placeholder_name].description || placeholder_name;
                appendTextNode(cell, text);
            } else {
                console.error(`Unknown column name: ${column}`);
            }
        }
    }

    // Apply button row
    if (PlaceholderData.auto_table_apply_button && columns.includes("input")) {
        // The row is only needed, if input elements are in the table
        const row = createChildElement(table_body, "tr");
        for (column of columns) {
            const cell = createChildElement(row, "td");

            if (column == "input") {
                const button = createChildElement(cell, "button");
                // const dbg_cntr = PlaceholderPlugin.increment_debug_counter();
                // debug(dbg_cntr, button);
        
                button.classList.add("placeholder-input-apply-button", "md-button", "md-button--primary");
                button.addEventListener("click", () => {
                    debug("Apply button clicked");
                    for (pre_apply_function of apply_actions) {
                        pre_apply_function();
                    }
                    PlaceholderPlugin.reload_page();
                });
                debug(`Apply button has ${apply_actions.length} actions assigned`);
                appendTextNode(button, "Apply new values");
            }
        }
    }

    PlaceholderPlugin.replace_placeholders_in_subtree(element);
}

PlaceholderPlugin.initialize_auto_tables = (used_placeholders) => {
    const element_list = document.querySelectorAll("div.auto-input-table");
    for (let element of element_list) {
        const columns_str = element.getAttribute("data-columns") || "name,input";
        const columns = columns_str.includes(",")? columns_str.split(",") : [columns_str];
        PlaceholderPlugin.generate_automatic_placeholder_table(element, columns, used_placeholders);
    }
};

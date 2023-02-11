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
        child = document.createElement(tag_name);
        parent.appendChild(child);
        return child;
    }

    info("Creating automatic input table at", element, "with columns", columns);
    // element.innerHTML = ""; // remove all children
    table = createChildElement(element, "table");
    table_head = createChildElement(table, "thead");
    table_head_row = createChildElement(table_head, "tr");
    table_body = createChildElement(table, "tbody");

    for (column of columns) {
        table_cell = createChildElement(table_head_row, "th");
        appendTextNode(table_cell, PlaceholderPlugin.TABLE_CELL_HEADINGS[column]);
    }

    for (placeholder_name of used_placeholders) {
        row = createChildElement(table_body, "tr");
        for (column of columns) {
            cell = createChildElement(row, "td");

            if (column == "name") {
                appendTextNode(cell, placeholder_name);
            } else if (column == "description") {
                appendTextNode(cell, PlaceholderData.description_map[placeholder_name]);
            } else if (column == "value") {
                appendTextNode(cell, `x${placeholder_name}x`);
            } else if (column == "input") {
                input = createChildElement(cell, "input");
                PlaceholderPlugin.prepare_input_field_for_placeholder(placeholder_name, input);
            } else if (column == "description-or-name") {
                const text = PlaceholderData.description_map[placeholder_name] || placeholder_name;
                appendTextNode(cell, text);
            } else {
                console.error(`Unknown column name: ${column}`);
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

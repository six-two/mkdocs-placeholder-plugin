import { logger } from "./debug";
import { prepare_input_field } from "./inputs";
import { InputTable, InputTableRow, Placeholder, PluginConfig } from "./parse_settings";
import { create_dynamic_placeholder_element } from "./replacer";

const TABLE_CELL_HEADINGS: Map<string, string> = new Map();
TABLE_CELL_HEADINGS.set("name", "Name");
TABLE_CELL_HEADINGS.set("description", "Description");
TABLE_CELL_HEADINGS.set("value", "Value");
TABLE_CELL_HEADINGS.set("input", "Input element");
TABLE_CELL_HEADINGS.set("description-or-name", "Description / name");

// Helper functions to simplify the following code
const appendTextNode = (element: Element, text: string): void => {
    element.appendChild(document.createTextNode(text));
}

const createChildElement = (parent: Element, tag_name: string): HTMLElement => {
    const child = document.createElement(tag_name);
    parent.appendChild(child);
    return child;
}

const generate_automatic_placeholder_table = (element: Element, columns: string[], config: PluginConfig, placeholders_to_show: Placeholder[]) => {
    placeholders_to_show = sort_and_remove_duplicate_placeholders(placeholders_to_show);
    
    // Remove the current contents. This enables the plugin to generate fallback contents in case the JavaScript code does not work
    element.innerHTML = "";

    if (placeholders_to_show.length == 0) {
        // Do not create an empty table. Instead show a warning on the page
        const div = createChildElement(element, "div");
        div.classList.add("info-message");
        if (placeholders_to_show.length == 0) {
            appendTextNode(div, "No placeholders to be shown")
        }
        return;
    }

    const details = createChildElement(element, "details");
    if (true) {
        // @TODO: make it a setting for user and site config
        details.setAttribute("open", "1");
    }

    const title = createChildElement(details, "summary");
    title.classList.add("auto-table-title");
    const title_text = createChildElement(title, "div");
    title_text.classList.add("text")
    appendTextNode(title_text, "Placeholders used on this page");
    const settings_button = createChildElement(title, "div");
    settings_button.onclick = (e: MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        alert("Not implemented yet!");
    };
    appendTextNode(settings_button, "⚙️")



    
    logger.info("Creating automatic input table at", element, "with columns", columns);
    // element.innerHTML = ""; // remove all children
    const table = createChildElement(details, "table");
    const table_head = createChildElement(table, "thead");
    const table_head_row = createChildElement(table_head, "tr");
    const table_body = createChildElement(table, "tbody");

    for (const column of columns) {
        const table_cell = createChildElement(table_head_row, "th");
        const heading = TABLE_CELL_HEADINGS.get(column);
        if (heading) {
            appendTextNode(table_cell, heading);
        } else {
            appendTextNode(table_cell, column);
            console.error(`Unknown column name: ${column}`);
        }
    }

    const rows: InputTableRow[] = [];
    for (const placeholder of placeholders_to_show) {
        if (placeholder.read_only) {
            logger.debug(`auto_table: Skipping ${placeholder.name} because it is read-only`)
            continue
        }
        const row = createChildElement(table_body, "tr");
        populate_auto_table_row(row, placeholder, columns, config);
        rows.push({
            "element": row,
            "placeholder": placeholder,
        });
    }

    config.input_tables.push({
        "columns": columns,
        "table_element": table,
        "rows": rows,
    });
}

const sort_and_remove_duplicate_placeholders = (placeholder_list: Placeholder[]): Placeholder[] => {
    return [...new Set(placeholder_list)].sort((a, b) => a.order_index - b.order_index);
}

const populate_auto_table_row = (row: HTMLElement, placeholder: Placeholder, columns: string[], config: PluginConfig) => {
    for (const column of columns) {
        const cell = createChildElement(row, "td");

        if (column == "name") {
            appendTextNode(cell, placeholder.name);
        } else if (column == "description") {
            appendTextNode(cell, placeholder.description);
        } else if (column == "value") {
            const dynamic_placeholer = create_dynamic_placeholder_element(placeholder);
            cell.appendChild(dynamic_placeholer);
            placeholder.output_elements.push(dynamic_placeholer);
        } else if (column == "input") {
            const input = createChildElement(cell, "input") as HTMLInputElement;
            prepare_input_field(config, placeholder, input);
        } else if (column == "description-or-name") {
            const text = placeholder.description || placeholder.name;
            appendTextNode(cell, text);
        } else {
            console.error(`Unknown column name: ${column}`);
        }
    }
}

const update_auto_table = (config: PluginConfig, table: InputTable, new_placeholder_list: Placeholder[]) => {
    // Sort them the same way they are sorted in the table -> lists are easy to compare
    new_placeholder_list = sort_and_remove_duplicate_placeholders(new_placeholder_list);

    // Step 1: remove rows that are no longer to be shown
    const rows_to_keep = [];
    for (const row of table.rows) {
        if (new_placeholder_list.includes(row.placeholder)) {
            rows_to_keep.push(row);
        } else {
            logger.debug(`Removed table row for ${row.placeholder.name}:`, row.element);
            row.element.remove();
        }
    }

    // Step 2: add rows that do not yet exist
    const final_rows: InputTableRow[] = [];
    const reversed_current: InputTableRow[] = [...rows_to_keep].reverse();
    const reversed_new: Placeholder[] = [...new_placeholder_list].reverse();

    let next_new;
    while (next_new = reversed_new.pop()) {
        // const next_new = reversed_new.pop();
        const next_current = reversed_current.slice(-1)[0];
        if (next_current && next_current.placeholder === next_new) {
            // The row is already in the table
            reversed_current.pop(); // remove from queue to keep in sync with other queue
            final_rows.push(next_current);
        } else {
            const element = document.createElement("tr");

            // insert at the correct position in the dom
            if (final_rows.length == 0) {
                // adds it before the first child or if it does not exist at the end (which would also be the first element :D)
                table.table_element.insertBefore(element, table.table_element.firstChild);
            } else {
                // insert it after the last row that was processed
                const last_node = final_rows[final_rows.length - 1].element;
                last_node.insertAdjacentElement("afterend", element);
            }

            populate_auto_table_row(element, next_new, table.columns, config);

            final_rows.push({
                "element": element,
                "placeholder": next_new,
            });

            logger.debug(`Added table row for ${next_new.name}:`, element);
        }
    }

    // Store the updated row information in the original table object
    table.rows = final_rows;
}

export const update_all_auto_tables = (config: PluginConfig) => {
    logger.debug(`Updating ${config.input_tables.length} automatic input tables`);
    if (config.input_tables.length > 0) {
        const new_placeholder_list = config.dependency_graph.get_all_used_placeholders();
        for (const table of config.input_tables) {
            update_auto_table(config, table, new_placeholder_list);
        }
    }
}

export const initialize_auto_tables = (config: PluginConfig) => {
    const element_list = document.querySelectorAll("div.auto-input-table");
    if (element_list.length > 0) {
        const used_placeholders = config.dependency_graph.get_all_used_placeholders().filter(x => !x.read_only);
        for (let element of element_list) {
            const columns_str = element.getAttribute("data-columns") || "name,input";
            const columns = columns_str.includes(",")? columns_str.split(",") : [columns_str];
            generate_automatic_placeholder_table(element, columns, config, used_placeholders);
        }
    }
};

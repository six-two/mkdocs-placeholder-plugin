import { logger } from "./debug";
import { prepare_input_field } from "./inputs";
import { Placeholder, PluginConfig } from "./parse_settings";
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
    
    logger.info("Creating automatic input table at", element, "with columns", columns);
    // element.innerHTML = ""; // remove all children
    const table = createChildElement(element, "table");
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

    for (const placeholder of placeholders_to_show) {
        if (placeholder.read_only) {
            logger.debug(`auto_table: Skipping ${placeholder.name} because it is read-only`)
            continue
        }
        const row = createChildElement(table_body, "tr");
        for (const column of columns) {
            const cell = createChildElement(row, "td");

            if (column == "name") {
                appendTextNode(cell, placeholder.name);
            } else if (column == "description") {
                appendTextNode(cell, placeholder.description);
            } else if (column == "value") {
                const dynamic_placeholer = create_dynamic_placeholder_element(placeholder);
                cell.appendChild(dynamic_placeholer);
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

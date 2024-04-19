import { logger } from "./debug";
import { register_inline_value_editors, unregister_inline_value_editors } from "./inline-inputs";
import { prepare_input_field } from "./inputs";
import { InputTable, InputTableRow, Placeholder, PluginConfig } from "./parse_settings";
import { create_dynamic_placeholder_element } from "./replacer";
import { clear_settings, clear_state, store_boolean_setting } from "./state_manager";

const TABLE_CELL_HEADINGS: Map<string, string> = new Map();
TABLE_CELL_HEADINGS.set("name", "Name");
TABLE_CELL_HEADINGS.set("description", "Description");
TABLE_CELL_HEADINGS.set("value", "Value");
TABLE_CELL_HEADINGS.set("input", "Input element");
TABLE_CELL_HEADINGS.set("description-or-name", "Description / name");

// Created myself, so no licensing issues should occur. Still, a decent unicode / font awesome icon may be better if it works across themes/operating systems/browsers
const GEAR_SVG = `<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
 <path id="svg_6" d="m7.79338,20.02127l0,0c0,-6.84327 5.74307,-12.39083 12.82751,-12.39083l0,0c3.40207,0 6.6648,1.30546 9.07042,3.62919c2.40563,2.32373 3.75709,5.47539 3.75709,8.76164l0,0c0,6.84327 -5.74307,12.39083 -12.82751,12.39083l0,0c-7.08444,0 -12.82751,-5.54757 -12.82751,-12.39083zm6.41376,0l0,0c0,3.42163 2.87154,6.19542 6.41376,6.19542c3.54222,0 6.41376,-2.77378 6.41376,-6.19542c0,-3.42163 -2.87154,-6.19542 -6.41376,-6.19542l0,0c-3.54222,0 -6.41376,2.77378 -6.41376,6.19542z" stroke="#fff" fill="#ffffff"/>
 <path id="svg_7" d="m17.46095,7.63098l1.2691,-5.24017l4.23035,0l1.2691,5.24017l-6.76856,0z" stroke="#fff" fill="#ffffff"/>
 <path transform="rotate(180, 20.9544, 35.1419)" id="svg_11" d="m17.57012,37.76199l1.2691,-5.24017l4.23035,0l1.2691,5.24017l-6.76856,0z" stroke="#fff" fill="#ffffff"/>
 <path transform="rotate(43, 31.5439, 9.59605)" id="svg_12" d="m28.15964,12.21614l1.2691,-5.24017l4.23035,0l1.2691,5.24017l-6.76856,0z" stroke="#fff" fill="#ffffff"/>
 <path transform="rotate(90, 35.9107, 19.8581)" id="svg_13" d="m32.52645,22.47815l1.2691,-5.24017l4.23035,0l1.2691,5.24017l-6.76856,0z" stroke="#fff" fill="#ffffff"/>
 <path transform="rotate(135, 31.7623, 30.2292)" id="svg_14" d="m28.37798,32.84933l1.2691,-5.24017l4.23035,0l1.2691,5.24017l-6.76856,0z" stroke="#fff" fill="#ffffff"/>
 <path transform="rotate(-45, 9.49152, 9.48688)" id="svg_15" d="m6.10724,12.10697l1.2691,-5.24017l4.23035,0l1.2691,5.24017l-6.76856,0z" stroke="#fff" fill="#ffffff"/>
 <path transform="rotate(-90, 5.01553, 19.9672)" id="svg_16" d="m1.63126,22.58732l1.2691,-5.24017l4.23035,0l1.2691,5.24017l-6.76856,0z" stroke="#fff" fill="#ffffff"/>
 <path transform="rotate(-135, 9.60069, 30.7751)" id="svg_17" d="m6.21641,33.39518l1.2691,-5.24017l4.23035,0l1.2691,5.24017l-6.76856,0z" stroke="#fff" fill="#ffffff"/>
</svg>`;

// Helper functions to simplify the following code
const appendTextNode = (element: Element, text: string): void => {
    element.appendChild(document.createTextNode(text));
}

const createChildElement = (parent: Element, tag_name: string): HTMLElement => {
    const child = document.createElement(tag_name);
    parent.appendChild(child);
    return child;
}

const convert_to_dynamic_placeholder_table = (config: PluginConfig, element: Element, content_element: Element) => {
    // Remove the current contents. This enables the plugin to generate fallback contents in case the JavaScript code does not work
    element.innerHTML = "";

    const title = createChildElement(element, "div");
    const title_text = createChildElement(title, "div");
    const settings_button = createChildElement(title, "div");
    
    const expandable_contents = createChildElement(element, "div");
    const settings_contents = createChildElement(expandable_contents, "div");
    expandable_contents.append(content_element);

    const update_expanded_state = (is_expanded: boolean) => {
        expandable_contents.style.display = is_expanded ? "flex" : "none";
        title_text.textContent = "Placeholders: Click here to " + (is_expanded ? "collapse" : "expand");
    }
    
    title.classList.add("auto-table-title");
    expandable_contents.classList.add("expandable_contents");
    settings_contents.classList.add("settings_contents");

    let expanded = config.settings.expand_auto_tables;
    update_expanded_state(expanded);
    title_text.addEventListener("click", () => {
        expanded = !expanded;
        update_expanded_state(expanded);
    });
    title_text.classList.add("text")

    prepare_settings_button(settings_button, settings_contents, () => {
        if (!expanded) {
            expanded = true;
            update_expanded_state(expanded);
        }
    });

    fill_settings_content_container(config, settings_contents);
}

const prepare_settings_button = (settings_button: HTMLElement, settings_contents: HTMLElement, expand_if_needed: () => void) => {
    let show_settings = false;
    settings_button.onclick = (e: MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();

        show_settings = !show_settings;
        settings_contents.style.display = show_settings ? "flex" : "none";

        if (show_settings) {
            expand_if_needed();
        }
    };
    settings_contents.style.display = show_settings ? "flex" : "none";
    settings_button.classList.add("settings_button");
    settings_button.innerHTML = GEAR_SVG;
    settings_button.title = "Hide / show settings"
}

const fill_settings_content_container = (config: PluginConfig, settings_contents: HTMLElement) => {
    const set_highlight_placeholders = (enabled: boolean) => {
        for (const placeholder of config.placeholders.values()) {
            for (const output of placeholder.output_elements) {
                if (enabled) {
                    output.classList.add("placeholder-value-highlighted");
                } else {
                    output.classList.remove("placeholder-value-highlighted");
                }
            }
        }
    };
    set_highlight_placeholders(config.settings.highlight_placeholders);

    const set_inline_editors_enabled = (enabled: boolean) => {
        if (enabled) {
            register_inline_value_editors(config);
        } else {
            unregister_inline_value_editors(config);
        }
    }

    createChildElement(settings_contents, "b").textContent = "Settings";
    // @TODO: later: when there are multiple settings dialogs, keep their values in sync
    append_boolean_setting_checkbox(settings_contents, config.settings.expand_auto_tables, "expand_auto_tables", "Expand placeholder tables by default*");
    append_boolean_setting_checkbox(settings_contents, config.settings.apply_change_on_focus_change, "apply_change_on_focus_change", "Apply value when focus changes away*");
    append_boolean_setting_checkbox(settings_contents, config.settings.debug, "debug", "Log JavaScript debug messages to console*");
    append_boolean_setting_checkbox(settings_contents, config.settings.highlight_placeholders, "highlight_placeholders", "Highlight placeholders (useful for debugging)", set_highlight_placeholders);
    append_boolean_setting_checkbox(settings_contents, config.settings.inline_editors, "inline_editors", "Allow editing placeholders directly in the page", set_inline_editors_enabled);
    createChildElement(settings_contents, "i").textContent = "* You need to reload the page for these settings to take effect."

    const settings_button_bar = createChildElement(settings_contents, "div");
    settings_button_bar.classList.add("button-bar");

    const settings_reset_button = createChildElement(settings_button_bar, "button");
    settings_reset_button.textContent = "Reset settings";
    settings_reset_button.addEventListener("click", clear_settings);

    const placeholder_reset_button = createChildElement(settings_button_bar, "button");
    placeholder_reset_button.textContent = "Reset all placeholders";
    placeholder_reset_button.addEventListener("click", clear_state);
}

const append_boolean_setting_checkbox = (parent_element: HTMLElement, value: boolean, name: string, label_text: string, custom_on_change = (enabled: boolean) => {}) => {
    const label = createChildElement(parent_element, "label");
    label.textContent = `${label_text} `;
    const checkbox = createChildElement(label, "input") as HTMLInputElement;
    checkbox.type = "checkbox";
    checkbox.checked = value;
    checkbox.addEventListener("change", () => {
        store_boolean_setting(name, checkbox.checked);
        custom_on_change(checkbox.checked);
    });
}


const generate_automatic_placeholder_table = (element: HTMLElement, columns: string[], config: PluginConfig, placeholders_to_show: Placeholder[], show_empty: boolean) => {
    placeholders_to_show = sort_and_remove_duplicate_placeholders(placeholders_to_show);

    const root_element = document.createElement("div");
    if (placeholders_to_show.length == 0) {
        if (show_empty) {
            root_element.textContent = "No placeholders to be shown";
        } else {
            // Remove the table placeholder
            element.remove();
            // No need constructing something that is never added to the DOM -> return immediately
            return;
        }
    } else {
        logger.info("Creating automatic input table at", element, "with columns", columns);

        root_element.classList.add("table-div")
        createChildElement(root_element, "b").innerHTML = "Enter different values in the table below and press <code>Enter</code> to update this page."

        const table = createChildElement(root_element, "table");
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

    // Wrap the result in a collapsible wrapper
    convert_to_dynamic_placeholder_table(config, element, root_element);
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
        for (const element of element_list) {
            if (element instanceof HTMLElement) {
                const columns_str = element.getAttribute("data-columns") || "name,input";
                const columns = columns_str.includes(",")? columns_str.split(",") : [columns_str];
                const show_empty = element.getAttribute("data-hide-empty") === null;
                generate_automatic_placeholder_table(element, columns, config, used_placeholders, show_empty);
            } else {
                console.warn("Element", element, "is expected to be an HTMLElement, but is not");
            }
        }
    }
};

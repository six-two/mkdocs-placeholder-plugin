import { logger, reload_page } from "./debug";
import { CheckboxPlaceholder, DropdownPlaceholder, InputType, Placeholder, PluginConfig, TextboxPlaceholder } from "./parse_settings";
import { replace_dynamic_placeholder_values } from "./replacer";
import { store_checkbox_state, store_dropdown_state, store_textbox_state } from "./state_manager";
import { validate_textbox_input_field } from "./validator";

export const initialize_all_input_fields = (config: PluginConfig): void => {
    const input_list: NodeListOf<HTMLInputElement> = document.querySelectorAll("input[data-input-for]");
    for (let input_element of input_list) {
        const placeholder_name = input_element.getAttribute("data-input-for");
        if (placeholder_name == null) {
            throw new Error("How can this be, the selector forces the 'data-input-for' attribute to exist");
        }
        
        const placeholder = config.placeholders.get(placeholder_name)
        if (placeholder) {
            prepare_input_field(config, placeholder, input_element);
        } else {
            console.warn(`Unknown placeholder referenced in input element: '${placeholder_name}'`);
            input_element.classList.add("input-for-variable");
            input_element.value = `ERROR_UNDEFINED_PLACEHOLDER: ${placeholder_name}`;
        }
    }
}

export const prepare_input_field = (config: PluginConfig, placeholder: Placeholder, input_element: HTMLInputElement): void => {
    input_element.classList.add("input-for-variable");

    if (placeholder.type == InputType.Checkbox) {
        initialize_input_checkbox(config, placeholder as CheckboxPlaceholder, input_element);
    } else if (placeholder.type == InputType.Dropdown) {
        initialize_input_dropdown(config, placeholder as DropdownPlaceholder, input_element);
    } else if (placeholder.type == InputType.Textbox) {
        initialize_input_textbox(config, placeholder as TextboxPlaceholder, input_element);
    } else {
        console.error(`Placeholder ${placeholder.name} has unknown type '${placeholder.type}'`);
    }
}

const initialize_input_checkbox = (config: PluginConfig, placeholder: CheckboxPlaceholder, input_element: HTMLInputElement): void => {
    input_element.type = "checkbox";
    input_element.checked = placeholder.current_is_checked;
    if (placeholder.read_only) {
        // disable the checkbox
        input_element.disabled = true;
    } else {
        // Listen for state changes
        input_element.addEventListener("change", () => {
            logger.debug("Checkbox change", placeholder.name, "- new value:", input_element.checked);
            store_checkbox_state(placeholder, input_element.checked);
            on_placeholder_change(config, placeholder);
        });
    }

    // Store this input element
    placeholder.input_elements.push(input_element);
}

const initialize_input_dropdown = (config: PluginConfig, placeholder: DropdownPlaceholder, input_element: HTMLInputElement): void => {
    const new_node: HTMLSelectElement = document.createElement("select");
    new_node.classList.add("placeholder-dropdown");

    for (const option of placeholder.options) {
        const option_element = document.createElement("option");
        option_element.text = option.display_name;
        new_node.appendChild(option_element);
    }
    // Replace input element entirely with the dropdown menu
    if (input_element.parentNode) {
        input_element.parentNode.replaceChild(new_node, input_element);
    } else {
        // How would we find it in the DOM if it has no parent?
        console.error(`Input element`, input_element, `for placeholder ${placeholder.name} has no parent!`);
    }

    // Select the stored option
    new_node.selectedIndex = placeholder.current_index;

    if (placeholder.read_only) {
        // disable the dropdown
        new_node.disabled = true;
    } else {
        // Add an event listener
        new_node.addEventListener("change", () => {
            logger.debug("Dropdown change", placeholder.name, "- new index:", new_node.selectedIndex);
            store_dropdown_state(placeholder, new_node.selectedIndex);
            on_placeholder_change(config, placeholder);
        });
    }

    // Store this input element
    placeholder.input_elements.push(new_node);
}

const initialize_input_textbox = (config: PluginConfig, placeholder: TextboxPlaceholder, input_element: HTMLInputElement): void => {
    // Restore the stored state
    input_element.value = placeholder.current_value;

    if (placeholder.read_only) {
        // disable the checkbox
        input_element.disabled = true;
        input_element.style.cursor = "not-allowed";
    } else {
        const on_keypress = (event: KeyboardEvent) => {
            if (event.key === "Enter") {
                logger.debug("Textbox change confirmed with Enter key for ", placeholder.name, "- new value:", input_element.value);
                if (validate_textbox_input_field(placeholder, input_element)) {
                    store_textbox_state(placeholder, input_element.value);
                    on_placeholder_change(config, placeholder);
                }
            } else if (event.key === "Escape") {
                // @TODO: why does this not get triggered? Is it intercepted by something else?
                logger.debug("Resetting input field for ", placeholder.name, " to current placeholder value");
                input_element.value = placeholder.current_value;
            }
        };

        if (placeholder.validators.length == 0) {
            // No validators -> no need to handle exception when validation fails
            input_element.addEventListener("keypress", on_keypress)
        } else {
            // Check if initial value is valid
            validate_textbox_input_field(placeholder, input_element);

            // Listen for state changes
            input_element.addEventListener("input", () => {
                // The text was probably modified, so we need to update the validator

                validate_textbox_input_field(placeholder, input_element);
            });
            input_element.addEventListener("keypress", on_keypress);
        }
    }

    // Store this input element
    placeholder.input_elements.push(input_element);
}


const on_placeholder_change = (config: PluginConfig, placeholder: Placeholder) => {
    const affected_placeholders = config.dependency_graph.get_all_upstream(placeholder);

    let require_reload = false;
    for (const ph of affected_placeholders) {
        require_reload = require_reload || ph.reload_page_on_change;
    }
    if (require_reload) {
        reload_page(); // for now we just use the full reload
    } else {
        config.dependency_graph.on_placeholder_value_change(placeholder);
        // @TODO: update auto-tables, since downstream may be changed

        // Update input elements
        for (const ph of affected_placeholders) {
            for (const input of ph.input_elements) {
                // @TODO: update
            }
        }

        // Update output elements
        replace_dynamic_placeholder_values(affected_placeholders);

        // reload_page(); // for now we just use the full reload
    }
}


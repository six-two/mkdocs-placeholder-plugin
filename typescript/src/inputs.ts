import { logger, reload_page } from "./debug";
import { CheckboxPlaceholder, DropdownPlaceholder, InputType, Placeholder, PluginConfig, TextboxPlaceholder } from "./parse_settings";
import { store_checkbox_state, store_dropdown_state, store_textbox_state } from "./state_manager";

export const initialize_input_fields = (config: PluginConfig): void => {
    const input_list: NodeListOf<HTMLInputElement> = document.querySelectorAll("input[data-input-for]");
    for (let input of input_list) {
        const placeholder_name = input.getAttribute("data-input-for");
        if (placeholder_name == null) {
            throw new Error("How can this be, the selector forces the 'data-input-for' attribute to exist");
        }
        input.classList.add("input-for-variable");
        const placeholder = config.placeholders.get(placeholder_name)

        if (placeholder) {
            if (placeholder.type == InputType.Checkbox) {
                initialize_input_checkbox(config, placeholder as CheckboxPlaceholder, input);
            } else if (placeholder.type == InputType.Dropdown) {
                initialize_input_dropdown(config, placeholder as DropdownPlaceholder, input);
            } else if (placeholder.type == InputType.Textbox) {
                initialize_input_textbox(config, placeholder as TextboxPlaceholder, input);
            } else {
                console.error(`Placeholder ${placeholder.name} has unknown type '${placeholder.type}'`);
            }
        } else {
            console.warn(`Unknown placeholder referenced in input element: '${placeholder_name}'`);
            input.value = `ERROR_UNDEFINED_PLACEHOLDER: ${placeholder_name}`;
        }
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
            on_placeholder_change(placeholder);
        });
    }

    // Store this input element
    placeholder.current_inputs.push(input_element);
}

const initialize_input_dropdown = (config: PluginConfig, placeholder: DropdownPlaceholder, input_element: HTMLInputElement): void => {
    const new_node = document.createElement("select");
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
            on_placeholder_change(placeholder);
        });
    }

    // Store this input element
    placeholder.current_inputs.push(new_node);
}

const initialize_input_textbox = (config: PluginConfig, placeholder: TextboxPlaceholder, input_element: HTMLInputElement): void => {
    // Restore the stored state
    input_element.value = placeholder.current_value;

    if (placeholder.read_only) {
        // disable the checkbox
        input_element.disabled = true;
        input_element.style.cursor = "not-allowed";
    } else {
        if (!placeholder.validators) {
            // No validators -> no need to handle exception when validation fails
            input_element.addEventListener("keypress", e => {
                if (e.key === "Enter") {
                    logger.debug("Textbox change confirmed with Enter key for ", placeholder.name, "- new value:", input_element.value);
                    store_textbox_state(placeholder, input_element.value);
                    on_placeholder_change(placeholder);
                } else if (e.key == "Escape") {
                    logger.debug("Resetting input field for ", placeholder.name, " to current placeholder value");
                    input_element.value = placeholder.current_value;
                }
            });
        } else {
            // Check if initial value is valid
            validate_textbox_input_field(placeholder, input_element);

            // Listen for state changes
            input_element.addEventListener("input", () => {
                validate_textbox_input_field(placeholder, input_element);
            });
            input_element.addEventListener("keypress", e => {
                if (e.key === "Enter") {
                    logger.debug("Textbox change confirmed with Enter key for ", placeholder.name, "- new value:", input_element.value);
                    if (validate_textbox_input_field(placeholder, input_element)) {
                        on_placeholder_change(placeholder);
                    }
                }
            });
        }
    }

    // Store this input element
    placeholder.current_inputs.push(input_element);
}

const validate_textbox_input_field = (placeholder: Placeholder, input_element: HTMLInputElement): boolean => {
    console.warn("@TODO: implement propperly: input validation");
    return true;// return whether the value can be accepted
}

const on_placeholder_change = (placeholder: Placeholder) => {
    // console.warn("@TODO: implement propperly: dynamic page updating");
    reload_page(); // for now we just use the full reload
}


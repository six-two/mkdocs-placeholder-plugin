import { update_all_auto_tables } from "./auto_tables";
import { logger, reload_page } from "./debug";
import { CheckboxPlaceholder, DropdownPlaceholder, InputType, Placeholder, PluginConfig, TextboxPlaceholder } from "./parse_settings";
import { replace_dynamic_placeholder_values } from "./replacer";
import { store_checkbox_state, store_dropdown_state, store_textbox_state } from "./state_manager";
import { validate_textbox_input_field } from "./validator";

export const initialize_all_input_fields = (config: PluginConfig): void => {
    const input_list: NodeListOf<HTMLInputElement> = document.querySelectorAll("input[data-input-for], select[data-input-for]");
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
    if (input_element.tagName != "INPUT") {
        console.warn(`Input element/tag for placeholder '${placeholder.name}' is expected to be INPUT, but is ${input_element.tagName}. Skipping`, input_element);
        return;
    }
    input_element.type = "checkbox";
    input_element.checked = placeholder.current_is_checked;
    if (placeholder.read_only) {
        // disable the checkbox
        input_element.disabled = true;
    } else {
        input_element.disabled = false;
        // Listen for state changes
        input_element.addEventListener("change", () => {
            logger.debug("Checkbox change", placeholder.name, "- new value:", input_element.checked);
            store_checkbox_state(placeholder, input_element.checked);
            placeholder.current_value = input_element.checked? placeholder.value_checked : placeholder.value_unchecked;
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
        option_element.text = option.display_name;// @TODO: allow placeholders in here
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
        new_node.disabled = false;
        // Add an event listener
        new_node.addEventListener("change", () => {
            logger.debug("Dropdown change", placeholder.name, "- new index:", new_node.selectedIndex);
            store_dropdown_state(placeholder, new_node.selectedIndex);
            placeholder.current_index = new_node.selectedIndex;
            placeholder.current_value = placeholder.options[new_node.selectedIndex].value;
            on_placeholder_change(config, placeholder);
        });
    }

    // Store this input element
    placeholder.input_elements.push(new_node);
}

const initialize_input_textbox = (config: PluginConfig, placeholder: TextboxPlaceholder, input_element: HTMLInputElement): void => {
    if (input_element.tagName != "INPUT") {
        console.warn(`Input element/tag for placeholder '${placeholder.name}' is expected to be INPUT, but is ${input_element.tagName}. Skipping`, input_element);
        return;
    }

    // Restore the stored state
    input_element.value = placeholder.current_value;

    if (placeholder.read_only) {
        // disable the checkbox
        input_element.disabled = true;
        input_element.style.cursor = "not-allowed";
    } else {
        input_element.disabled = false;
        if (placeholder.default_value != undefined) {
            input_element.placeholder = `Default: ${placeholder.default_value}`;
        } else {
            input_element.placeholder = "Dynamic default value";
        }

        const confirm_change = () => {
            if (placeholder.current_value == input_element.value) {
                logger.debug(`Value for placeholder ${placeholder.name} was not changed`);
            } else {
                // Expensive actions, only perform them if the value was actually changed
                if (validate_textbox_input_field(placeholder, input_element)) {
                    store_textbox_state(placeholder, input_element.value);
                    placeholder.current_value = input_element.value;
                    on_placeholder_change(config, placeholder);

                    // The new value is applied, so it now is the same as the stored one
                    input_element.classList.remove("value-modified");
                }
            }
        }

        // Check if initial value is valid and initialize the tooltip
        validate_textbox_input_field(placeholder, input_element);

        // Listen for state changes
        input_element.addEventListener("input", () => {
            // The text was probably modified, so we need to update the validator
            validate_textbox_input_field(placeholder, input_element);

            // Update the changed status of the placeholder
            if (input_element.value == placeholder.current_value) {
                input_element.classList.remove("value-modified");
            } else {
                input_element.classList.add("value-modified");
            }
        });

        input_element.addEventListener("keypress", (event: KeyboardEvent) => {
            if (event.key === "Enter") {
                logger.debug("Textbox change confirmed with Enter key for", placeholder.name, "- new value:", input_element.value);
                confirm_change();
            }
        });
        input_element.addEventListener("keydown", (event: KeyboardEvent) => {
            // I have no idea, why Escape does not work with the keypress event (Safari on MacOS). As a work aroud, we listen to the keydown event
            if (event.key === "Escape") {
                logger.debug("Resetting input field for ", placeholder.name, " to current placeholder value");
                input_element.value = placeholder.current_value;
            }
        });
        input_element.addEventListener("focusout", () => {
            // The value may change on the fly (use changes settings), so we can not just conditionally add the event listener, but need to check each time
            if (config.settings.apply_change_on_focus_change) {
                logger.debug("Textbox change confirmed by changing focus", placeholder.name, "- new value:", input_element.value);
                confirm_change();
            }
        })
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

    logger.debug(`Change of ${placeholder.name} requires updates for placeholders:\n${affected_placeholders.map(p => ` - ${p.name}\n`).join("")}\nRequires reload: ${require_reload}`);
    if (require_reload) {
        reload_page(); // for now we just use the full reload
    } else {
        config.dependency_graph.on_placeholder_value_change(placeholder);

        // update auto-tables, since downstream may be changed
        update_all_auto_tables(config);

        // Update all input elements for the modified placeholder
        if (placeholder.type == InputType.Checkbox) {
            const ph = placeholder as CheckboxPlaceholder;
            for (const input_element of ph.input_elements) {
                input_element.checked = ph.current_is_checked;
            }
        } else if (placeholder.type == InputType.Dropdown) {
            const ph = placeholder as DropdownPlaceholder;
            for (const input_element of ph.input_elements) {
                input_element.selectedIndex = ph.current_index;
            }
        } else if (placeholder.type == InputType.Textbox) {
            const ph = placeholder as TextboxPlaceholder;
            for (const input_element of ph.input_elements) {
                input_element.value = ph.current_value;
                validate_textbox_input_field(ph, input_element);
            }
        } else {
            console.warn(`Placeholder ${placeholder.name} has unexpected type '${placeholder.type}'`);            
        }

        // @TODO Not needed as long as the dropdown display name is static
        // // Update input elements
        // for (const ph of affected_placeholders) {
        //     // Only dropdown's input elements can depend on other placeholders (the label)
        //     if (ph.type == InputType.Dropdown) {
        //         for (const input of (ph as DropdownPlaceholder).input_elements) {
        //             // code here
        //         }
        //     }
        // }

        // Update output elements
        replace_dynamic_placeholder_values(affected_placeholders);
    }
}


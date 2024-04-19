import { PluginConfig, InputType, TextboxPlaceholder } from "./parse_settings";
import { logger } from "./debug";
import { validate_textbox_editable_span } from "./validator";
import { on_placeholder_change } from "./inputs";
import { store_textbox_state } from "./state_manager";


export const register_inline_value_editors = (config: PluginConfig) => {
    const placeholder_value_elements = document.querySelectorAll("span.placeholder-value[data-placeholder]");
    for (const element of placeholder_value_elements) {
        const placeholder_name = element.getAttribute("data-placeholder");
        console.debug("patching", placeholder_name, element);
        if (placeholder_name) {
            // ^-- Should always be true, since we check for it in our query
            const placeholder = config.placeholders.get(placeholder_name);
            if (placeholder) {
                if (!placeholder.read_only) {
                    if (placeholder.type == InputType.Textbox) {
                        // Textboxes should be the easiest, the other ones might be a bit of a headache
                        prepare_span_for_textbox_editor(config, element as HTMLSpanElement, placeholder as TextboxPlaceholder);
                    }
                }
            } else {
                console.warn(`Unknown placeholder referenced in input element: '${placeholder_name}'`, element);
            }
        }
    }
}


const prepare_span_for_textbox_editor = (config: PluginConfig, input_element: HTMLSpanElement, placeholder: TextboxPlaceholder) => {
    // This lets users actually modify the span like an input element
    input_element.contentEditable = "true";

    // Add a special class for styling
    input_element.classList.add("placeholder-value-editable");

    // copy paste from inputs.ts @TODO clean up/deduplicate
    const confirm_change = () => {
        if (placeholder.current_value == input_element.innerText) {
            logger.debug(`Value for placeholder ${placeholder.name} was not changed`);
        } else {
            // Expensive actions, only perform them if the value was actually changed
            if (validate_textbox_editable_span(placeholder, input_element)) {
                store_textbox_state(placeholder, input_element.innerText);
                placeholder.current_value = input_element.innerText;
                on_placeholder_change(config, placeholder);

                // The new value is applied, so it now is the same as the stored one
                input_element.classList.remove("value-modified");
            }
        }
    }

    // Check if initial value is valid and initialize the tooltip
    validate_textbox_editable_span(placeholder, input_element);

    // Listen for state changes
    input_element.addEventListener("input", () => {
        // The text was probably modified, so we need to update the validator
        validate_textbox_editable_span(placeholder, input_element);

        // Update the changed status of the placeholder
        if (input_element.innerText == placeholder.current_value) {
            input_element.classList.remove("value-modified");
        } else {
            input_element.classList.add("value-modified");
        }
    });

    input_element.addEventListener("keypress", (event: KeyboardEvent) => {
        if (event.key === "Enter") {
            // prevent inserting a line break
            event.preventDefault();

            logger.debug("Textbox change confirmed with Enter key for", placeholder.name, "- new value:", input_element.innerText);
            confirm_change();
        }
    });
    input_element.addEventListener("keydown", (event: KeyboardEvent) => {
        // I have no idea, why Escape does not work with the keypress event (Safari on MacOS). As a work around, we listen to the keydown event
        if (event.key === "Escape") {
            logger.debug("Resetting input field for ", placeholder.name, " to current placeholder value");
            input_element.innerText = placeholder.current_value;

            // reset the validation state
            validate_textbox_editable_span(placeholder, input_element);
            input_element.classList.remove("value-modified");
        }
    });
    input_element.addEventListener("focusout", () => {
        // The value may change on the fly (use changes settings), so we can not just conditionally add the event listener, but need to check each time
        if (config.settings.apply_change_on_focus_change) {
            logger.debug("Textbox change confirmed by changing focus", placeholder.name, "- new value:", input_element.innerText);
            confirm_change();
        }
    })
}

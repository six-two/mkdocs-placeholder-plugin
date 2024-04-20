import { PluginConfig, InputType, TextboxPlaceholder, CheckboxPlaceholder } from "./parse_settings";
import { logger } from "./debug";
import { validate_textbox_editable_span } from "./validator";
import { on_placeholder_change } from "./inputs";
import { store_textbox_state, store_checkbox_state } from "./state_manager";


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
                    } else if (placeholder.type == InputType.Checkbox) {
                        // Checkboxes might be even easier, we click them to toggle
                        prepare_span_for_checkbox_editor(config, element as HTMLSpanElement, placeholder as CheckboxPlaceholder);
                    }

                }
            } else {
                console.warn(`Unknown placeholder referenced in input element: '${placeholder_name}'`, element);
            }
        }
    }
}

export const unregister_inline_value_editors = (config: PluginConfig) => {
    const placeholder_value_elements = document.querySelectorAll("span.placeholder-value-editable,span.placeholder-value-checkbox");

    // Remove all previously added event listeners
    config.event_listener_abort_controller.abort();

    // Replace the now triggered abort controller with a new one
    config.event_listener_abort_controller = new AbortController();

    // Remove the specific classes and editable attribute that the register method added
    for (const element of placeholder_value_elements) {
        const span_element = element as HTMLSpanElement;
        span_element.classList.remove("placeholder-value-editable", "placeholder-value-checkbox", "validation-error", "validation-warn", "validation-ok", "validation-none");
        // make it non-editable (only affects textbox placeholders)
        span_element.contentEditable = "false";
        // remove the tooltip
        span_element.title = "";
    }
}

const prepare_span_for_checkbox_editor = (config: PluginConfig, input_element: HTMLSpanElement, placeholder: CheckboxPlaceholder) => {
    input_element.classList.add("placeholder-value-checkbox");

    const abort_signal_object = { signal: config.event_listener_abort_controller.signal };

    const description = placeholder.description ? `\nDescription: ${placeholder.description}` : "";
    input_element.title = `Placeholder name: ${placeholder.name}${description}\nUsage: Click to toggle the value`;

    input_element.addEventListener("click", (event: MouseEvent) => {
        // toggle checkbox state
        const new_value = !placeholder.current_is_checked;
        placeholder.current_value = new_value ? placeholder.value_checked : placeholder.value_unchecked;
        logger.debug("Checkbox change", placeholder.name, "- new value:", new_value);

        store_checkbox_state(placeholder, new_value);
        on_placeholder_change(config, placeholder);
    }, abort_signal_object);
}

const prepare_span_for_textbox_editor = (config: PluginConfig, input_element: HTMLSpanElement, placeholder: TextboxPlaceholder) => {
    // This lets users actually modify the span like an input element
    input_element.contentEditable = "true";

    // Add a special class for styling
    input_element.classList.add("placeholder-value-editable");

    const abort_signal_object = { signal: config.event_listener_abort_controller.signal };

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

    const description = placeholder.description ? `\nDescription: ${placeholder.description}` : "";
    const tooltip_when_not_focused = `Placeholder name: ${placeholder.name}${description}\nDefault value: ${placeholder.default_value}\nUsage: Click to edit the value. Leaving the text field or pressing enter will store the new value, pressing Escape will revert current changes.`; // @TODO: what if only a function is defined?

    // Check if initial value is valid and initialize the tooltip
    validate_textbox_editable_span(placeholder, input_element);
    input_element.title = tooltip_when_not_focused;

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
    }, abort_signal_object);

    input_element.addEventListener("keypress", (event: KeyboardEvent) => {
        if (event.key === "Enter") {
            // prevent inserting a line break
            event.preventDefault();

            logger.debug("Textbox change confirmed with Enter key for", placeholder.name, "- new value:", input_element.innerText);
            confirm_change();
        }
    }, abort_signal_object);
    input_element.addEventListener("keydown", (event: KeyboardEvent) => {
        // I have no idea, why Escape does not work with the keypress event (Safari on MacOS). As a work around, we listen to the keydown event
        if (event.key === "Escape") {
            logger.debug("Resetting input field for ", placeholder.name, " to current placeholder value");
            input_element.innerText = placeholder.current_value;

            // reset the validation state
            validate_textbox_editable_span(placeholder, input_element);
            input_element.classList.remove("value-modified");
        }
    }, abort_signal_object);
    input_element.addEventListener("focusout", () => {
        // The value may change on the fly (use changes settings), so we can not just conditionally add the event listener, but need to check each time
        if (config.settings.apply_change_on_focus_change) {
            logger.debug("Textbox change confirmed by changing focus", placeholder.name, "- new value:", input_element.innerText);
            confirm_change();
        }
        // restore the original tooltip
        input_element.title = tooltip_when_not_focused;
    }, abort_signal_object)
    input_element.addEventListener("focusin", () => {
        // show the validation popup instead
        validate_textbox_editable_span(placeholder, input_element);
    }, abort_signal_object)
}

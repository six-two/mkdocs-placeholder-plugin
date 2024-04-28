import { PluginConfig, TextboxPlaceholder } from "../parse_settings";
import { logger } from "../debug";
import { validate_textbox_editable_span } from "../validator";
import { on_placeholder_change } from "../inputs";
import { store_textbox_state } from "../state_manager";

export const prepare_span_for_textbox_editor = (config: PluginConfig, input_element: HTMLSpanElement, placeholder: TextboxPlaceholder) => {
    // We need to set this so that the element can obtain focus.
    input_element.tabIndex = 0;

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
    const tooltip_when_not_focused = `Placeholder name: ${placeholder.name}${description}\nDefault value: ${placeholder.default_value}\nUsage: Click to edit the value. Leaving the text field or pressing enter will store the new value, pressing Escape will revert current changes. While editing the field, the tooltip will show warnings/errors if your value is not what is expected`; // @TODO: what if only a function is defined?

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
        logger.debug("Focus lost");

        // The value may change on the fly (use changes settings), so we can not just conditionally add the event listener, but need to check each time
        if (config.settings.apply_change_on_focus_change) {
            logger.debug("Textbox change confirmed by changing focus", placeholder.name, "- new value:", input_element.innerText);
            confirm_change();
        }
        // restore the original tooltip
        input_element.title = tooltip_when_not_focused;

        // disable editing to make selecting (part of the) text work
        input_element.contentEditable = "false";

        // Remove the selection range (by default entire element)
        window.getSelection()?.removeAllRanges();
    }, abort_signal_object)

    input_element.addEventListener("focusin", () => {
        logger.debug("Focus gained");

        // This lets users actually modify the span like an input element
        input_element.contentEditable = "true";
        // show the validation popup instead
        validate_textbox_editable_span(placeholder, input_element);

        // Check if the browser supports the Selection and Range APIs
        if (window.getSelection && document.createRange) {
            // Select the whole contents of the element when it gains focus. This is required for tabbing into the element to create a cursor.
            // It also makes it quicker to replace the whole value of an element.
            const selection = window.getSelection();
            if (selection && selection.focusNode != input_element) {
                const range = document.createRange();
                // Set the range to the end of the element
                range.selectNodeContents(input_element);

                // Remove any existing selections
                if (selection.rangeCount > 0) {
                    selection.removeAllRanges();
                }
                // Add the new range to the selection
                selection.addRange(range);
            }
        }
    }, abort_signal_object)
}

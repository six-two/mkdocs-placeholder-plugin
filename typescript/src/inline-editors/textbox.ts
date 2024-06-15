import { PluginConfig, TextboxPlaceholder } from "../parse_settings";
import { logger } from "../debug";
import { validate_textbox_editable_span, validate_placeholder_value, PlaceholderValidatity } from "../validator";
import { on_placeholder_change } from "../inputs";
import { store_textbox_state } from "../state_manager";
import { change_text_keep_other_children } from "../replacer";

// Source: https://pictogrammers.com/library/mdi/icon/pencil/
const PEN_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z" /></svg>';

const add_icon_back_if_user_deleted_it = (input_element: HTMLSpanElement) => {
    if (!input_element.querySelector(".inline-editor-icon-span")) {
        // The icon was deleted, the user probably uses firefox
        // we just quickly recreate the icon
        const icon = document.createElement("span");
        icon.classList.add("inline-editor-icon-span");
        icon.contentEditable = "false";
        icon.innerHTML = PEN_SVG;
        input_element.appendChild(icon);
    }

    // Make sure that text is not on both sides of the icon
    const text_nodes = []
    for (const child of input_element.childNodes) {
        if (child.nodeType === Node.TEXT_NODE) {
            text_nodes.push(child);
        }
    }

    let combined_text = "";
    if (text_nodes.length > 1 || input_element.firstChild?.nodeType != Node.TEXT_NODE) {
        // the user entered something after the icon :/
        for (const text_child of text_nodes) {
            combined_text += text_child.textContent;
            text_child.remove();
        }
        input_element.insertAdjacentText("afterbegin", combined_text);
    }

}

export const prepare_span_for_textbox_editor = (config: PluginConfig, input_element: HTMLSpanElement, placeholder: TextboxPlaceholder) => {
    // We need to set this so that the element can obtain focus.
    input_element.tabIndex = 0;

    // Stop browsers from trying to be smart
    input_element.spellcheck = false;
    input_element.translate = false;
    input_element.autocapitalize = "off";

    // Add a special class for styling
    input_element.classList.add("placeholder-value-editable");

    // There should be only one, but this prevents crashes if there are more or even none
    input_element.querySelectorAll(".inline-editor-icon-span").forEach(icon => {icon.innerHTML = PEN_SVG});

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

    // Check if initial value is valid and initialize the tooltip
    validate_textbox_editable_span(placeholder, input_element);
    input_element.title = placeholder.default_tooltip;

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

        add_icon_back_if_user_deleted_it(input_element);
    }, abort_signal_object);

    input_element.addEventListener("keypress", (event: KeyboardEvent) => {
        if (event.key === "Enter") {
            // prevent inserting a line break
            event.preventDefault();

            logger.debug("Textbox change confirmed with Enter key for", placeholder.name, "- new value:", input_element.innerText);
            confirm_change();
            select_all_text_in_element(input_element);
        }
    }, abort_signal_object);

    input_element.addEventListener("keydown", (event: KeyboardEvent) => {
        // I have no idea, why Escape does not work with the keypress event (Safari on MacOS). As a work around, we listen to the keydown event
        if (event.key === "Escape") {
            logger.debug("Resetting input field for ", placeholder.name, " to current placeholder value");
            change_text_keep_other_children(input_element, placeholder.current_value);

            // reset the validation state
            validate_textbox_editable_span(placeholder, input_element);
            input_element.classList.remove("value-modified");
            select_all_text_in_element(input_element);
        }
    }, abort_signal_object);

    input_element.addEventListener("focusout", () => {
        logger.debug("Focus lost");

        // The value may change on the fly (use changes settings), so we can not just conditionally add the event listener, but need to check each time
        if (config.settings.apply_change_on_focus_change) {
            logger.debug("Textbox change confirmed by changing focus", placeholder.name, "- new value:", input_element.innerText);
            confirm_change();
        }
        // if there are no validation warnings or errors, restore the original tooltip for all inline editors (since they are updated to reflect the validation status)
        const validation_result = validate_placeholder_value(placeholder, input_element.innerText);
        if (validation_result.rating == PlaceholderValidatity.Good || validation_result.rating == PlaceholderValidatity.NoValidator) {
            for (const element of placeholder.output_elements) {
                if (element.classList.contains("placeholder-value-editable")) {
                    element.title = placeholder.default_tooltip;
                }
            }
        }

        // disable editing to make selecting (part of the) text work
        input_element.contentEditable = "false";

        // Remove the selection range (by default entire element)
        window.getSelection()?.removeAllRanges();
    }, abort_signal_object)

    input_element.addEventListener("focusin", () => {
        logger.debug("Focus gained");

        // This lets users actually modify the span like an input element
        // Because firefox does not support this attribute, we need to do exception handling and fall back to the one it supports
        try {
            input_element.contentEditable = "plaintext-only";
        } catch {
            input_element.contentEditable = "true";
        }
        // show the validation popup instead
        validate_textbox_editable_span(placeholder, input_element);

        // Select the whole contents of the element when it gains focus. This is required for tabbing into the element to create a cursor.
        // It also makes it quicker to replace the whole value of an element.
        select_all_text_in_element(input_element);
    }, abort_signal_object)
}

let shown_no_selection_warning = false;
const select_all_text_in_element = (element: HTMLElement) => {
    // Check if the browser supports the Selection and Range APIs
    if (window.getSelection && document.createRange) {
        const selection = window.getSelection();
        if (selection) {
            selection.removeAllRanges();
            
            const range = document.createRange();
            range.selectNodeContents(element);
            selection.addRange(range);
        } else if (!shown_no_selection_warning) {
            shown_no_selection_warning = true;
            console.warn("getSelection returned null");
        }
    } else {
        if (!shown_no_selection_warning) {
            shown_no_selection_warning = true;
            console.warn("Can not set selection, because window.getSelection or document.createRange are not supported");
        }
    }
}

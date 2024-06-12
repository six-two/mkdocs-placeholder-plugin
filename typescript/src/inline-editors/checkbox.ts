import { PluginConfig, CheckboxPlaceholder } from "../parse_settings";
import { logger } from "../debug";
import { on_placeholder_change } from "../inputs";
import { store_checkbox_state } from "../state_manager";

// Source: https://pictogrammers.com/library/mdi/icon/checkbox-outline/
const CHECKED_SVG_URL = '<svg class="checkbox-checked" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>checkbox-outline</title><path d="M19,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M19,5V19H5V5H19M10,17L6,13L7.41,11.58L10,14.17L16.59,7.58L18,9" /></svg>'

// Source: https://pictogrammers.com/library/mdi/icon/checkbox-blank-outline/
const UNCHECKED_SVG_URL = '<svg class="checkbox-unchecked" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>checkbox-blank-outline</title><path d="M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M19,5V19H5V5H19Z" /></svg>'

export const update_inline_checkbox_editor_classes = (element: HTMLElement, placeholder: CheckboxPlaceholder) => {
    // these classes can be used to show the current state with inline placeholders
    if (placeholder.current_is_checked) {
        element.classList.add("checked");
        element.classList.remove("unchecked");
    } else {
        element.classList.add("unchecked");
        element.classList.remove("checked");
    }
}


export const prepare_span_for_checkbox_editor = (config: PluginConfig, input_element: HTMLSpanElement, placeholder: CheckboxPlaceholder) => {
    input_element.classList.add("placeholder-value-checkbox");

    // There should be only one, but this prevents crashes if there are more or even none
    input_element.querySelectorAll(".inline-editor-icon-span").forEach(icon => {icon.innerHTML = CHECKED_SVG_URL + UNCHECKED_SVG_URL});

    input_element.setAttribute("tabindex", "0");

    const abort_signal_object = { signal: config.event_listener_abort_controller.signal };

    const description = placeholder.description ? `\nDescription: ${placeholder.description}` : "";
    input_element.title = `Placeholder name: ${placeholder.name}${description}\nUsage: Click to toggle the value. You can also press Enter if the placeholder is focused.`;

    const fn_change_value = () => {
        // toggle checkbox state
        const new_value = !placeholder.current_is_checked;
        placeholder.current_value = new_value ? placeholder.value_checked : placeholder.value_unchecked;
        logger.debug("Checkbox change", placeholder.name, "- new value:", new_value);

        store_checkbox_state(placeholder, new_value);
        on_placeholder_change(config, placeholder);
    }

    input_element.addEventListener("click", fn_change_value, abort_signal_object);
    input_element.addEventListener("keydown", (event: KeyboardEvent) => {
        if (event.key === "Enter") {
            fn_change_value();
            event.preventDefault();
         }
    }, abort_signal_object);

    update_inline_checkbox_editor_classes(input_element, placeholder);
}


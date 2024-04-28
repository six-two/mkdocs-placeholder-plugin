import { PluginConfig, CheckboxPlaceholder } from "../parse_settings";
import { logger } from "../debug";
import { on_placeholder_change } from "../inputs";
import { store_checkbox_state } from "../state_manager";



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


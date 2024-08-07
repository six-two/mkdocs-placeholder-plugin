import { PluginConfig, InputType, TextboxPlaceholder, CheckboxPlaceholder, DropdownPlaceholder, VALID_INLINE_EDITOR_STYLES } from "../parse_settings";
import { prepare_span_for_checkbox_editor } from "./checkbox";
import { prepare_span_for_dropdown_editor } from "./dropdown";
import { prepare_span_for_textbox_editor } from "./textbox";

export const register_inline_value_editors = (config: PluginConfig) => {
    // Ensure that the correct class is set before the editors are created
    set_inline_editor_style(config.settings.inline_editor_style);

    const placeholder_value_elements = document.querySelectorAll("span.placeholder-value.inline-editor-requested[data-placeholder]");
    for (const element of placeholder_value_elements) {
        const placeholder_name = element.getAttribute("data-placeholder");
        if (placeholder_name) {
            // ^-- Should always be true, since we check for it in our query
            const placeholder = config.placeholders.get(placeholder_name);
            if (placeholder) {
                if (!placeholder.read_only) {
                    element.classList.add("placeholder-value-any");

                    const icon = document.createElement("span");
                    icon.classList.add("inline-editor-icon-span");
                    icon.contentEditable = "false";
                    element.appendChild(icon);

                    if (placeholder.type == InputType.Textbox) {
                        prepare_span_for_textbox_editor(config, element as HTMLSpanElement, placeholder as TextboxPlaceholder);
                    } else if (placeholder.type == InputType.Checkbox) {
                        prepare_span_for_checkbox_editor(config, element as HTMLSpanElement, placeholder as CheckboxPlaceholder);
                    } else if (placeholder.type == InputType.Dropdown) {
                        prepare_span_for_dropdown_editor(config, element as HTMLSpanElement, placeholder as DropdownPlaceholder);
                    }
                }
            } else {
                console.warn(`Unknown placeholder referenced in input element: '${placeholder_name}'`, element);
            }
        }
    }
}

export const unregister_inline_value_editors = (config: PluginConfig) => {
    const placeholder_value_elements = document.querySelectorAll("span.placeholder-value-editable, span.placeholder-value-checkbox, span.placeholder-value-dropdown");

    // Remove all previously added event listeners
    config.event_listener_abort_controller.abort();

    // Replace the now triggered abort controller with a new one
    config.event_listener_abort_controller = new AbortController();

    // Remove the specific classes and editable attribute that the register method added
    for (const element of placeholder_value_elements) {
        const span_element = element as HTMLSpanElement;
        span_element.classList.remove("placeholder-value-editable", "placeholder-value-checkbox", "placeholder-value-dropdown", "placeholder-value-any", "validation-error", "validation-warn", "validation-ok", "validation-none");
        // make it non-editable (only affects textbox placeholders)
        span_element.contentEditable = "false";
        // remove the tooltip
        span_element.title = "";
        // remove the ability to focus them via tab
        span_element.removeAttribute("tabindex");
        // remove the icon
        span_element.querySelectorAll(".inline-editor-icon-span").forEach(icon => icon.remove());
    }
}

export const set_inline_editor_style = (style: string) => {
    if (VALID_INLINE_EDITOR_STYLES.includes(style)) {
        // We add the class to the body, so that it will apply to all placeholders (at once)
        for (const style_to_remove of VALID_INLINE_EDITOR_STYLES) {
            document.body.classList.remove(`inline-editor-${style_to_remove}`);
        }
        document.body.classList.add(`inline-editor-${style}`);
    } else {
        console.error(`Tried to set inline editor style '${style}', but only ${VALID_INLINE_EDITOR_STYLES} are allowed`);
    }
}


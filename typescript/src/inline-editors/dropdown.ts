import { PluginConfig, DropdownPlaceholder } from "../parse_settings";
import { on_placeholder_change } from "../inputs";
import { store_dropdown_state } from "../state_manager";


export const prepare_span_for_dropdown_editor = (config: PluginConfig, input_element: HTMLSpanElement, placeholder: DropdownPlaceholder) => {
    input_element.classList.add("placeholder-value-dropdown");

    input_element.setAttribute("tabindex", "0");

    const abort_signal_object = { signal: config.event_listener_abort_controller.signal };

    const description = placeholder.description ? `\nDescription: ${placeholder.description}` : "";
    let tooltip = `Placeholder name: ${placeholder.name}${description}\nDefault option: ${placeholder.options[placeholder.default_index].value}\nUsage: (left-)click to cycle forward through the values, right-click to cycle through backwards. You can also use the Enter, Up, and Down keys if the placeholder is selected.\nPossible values:`;

    for (const option of placeholder.options) {
        tooltip += `\n- ${option.value}`;
    }

    input_element.title = tooltip;

    const modify_index_by = (count: number) => {
        let index = (placeholder.current_index + count) % placeholder.options.length;
        if (index < 0) {
            index += placeholder.options.length;
        }
        store_dropdown_state(placeholder, index);
        placeholder.current_index = index;
        placeholder.current_value = placeholder.options[index].value;
        on_placeholder_change(config, placeholder);
    }

    // Showing an inline dropdown modifies the layout too much and binding it to events like click, mouseenter, etc is problematic. Thus this seems to be the simplest and least buggy solution.
    input_element.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        modify_index_by(1);
    }, abort_signal_object);

    input_element.addEventListener("contextmenu", (event) => {
        // prevent right click menu
        event.preventDefault();
        event.stopPropagation();
        modify_index_by(-1);
    }, abort_signal_object);

    input_element.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === "ArrowDown") {
            modify_index_by(1);
            event.preventDefault();
        } else if (event.key === 'ArrowUp') {
            modify_index_by(-1);
            event.preventDefault();
        }
    }, abort_signal_object);
}

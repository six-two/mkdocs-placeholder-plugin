import { CheckboxPlaceholder, DropdownPlaceholder } from "./parse_settings";

// These functions are here to make it easier to change the storage backend (for example locasstorage -> cookies)
// and to make it possible to potentially have better debugging
const STORAGE_PREFIX = "PLACEHOLDER_"; // @TODO make it configurable by settings?

const store_value = (name: string, value: string): void => {
    localStorage.setItem(STORAGE_PREFIX + name, value);
}

const load_value = (name: string): string | null => {
    return localStorage.getItem(STORAGE_PREFIX + name)
}

// I changed the storage model: the real value is stored in the placeholder object instead of in localstorage -> easier and safer to access

// We pass the whole placeholder instead of just a name, so that you can not accidentally call the wrong function or use an invalid placeholder name
// We use different values for different types (checkbox -> NAME_IS_CHECKED, textbox -> NAME_TEXT, ...) so that if a user changes the type of a placeholder it should not cause problems
export const store_checkbox_state = (placeholder: CheckboxPlaceholder, new_is_checked: boolean): void => {
    // Update the placeholder's value
    placeholder.current_is_checked = new_is_checked;
    placeholder.current_value = new_is_checked? placeholder.value_checked : placeholder.value_unchecked;
    // Permanently store the new state
    store_value(`${placeholder.name}_IS_CHECKED`, new_is_checked? "1" : "0");
}

export const load_checkbox_state = (placeholder: CheckboxPlaceholder): void => {
    const stored_state = load_value(`${placeholder.name}_IS_CHECKED`);
    if (stored_state == null) {
        // No stored state -> use default value
        placeholder.current_is_checked = placeholder.checked_by_default;
    } else {
        if (stored_state == "0" || stored_state == "1") {
            // Load the stored state
            placeholder.current_is_checked = stored_state == "1";
        } else {
            // Unexpected state, warn user and fall back to default
            console.warn(`Unexpected state for checkbox. Should be '0' or '1', but was '${stored_state}'`);
            placeholder.current_is_checked = placeholder.checked_by_default;
        }
    }
    
    // Now we update the actual value based on the state
    placeholder.current_value = placeholder.current_is_checked? placeholder.value_checked : placeholder.value_unchecked;
}

const is_valid_index = (placeholder: DropdownPlaceholder, index: number): boolean => {
    try {
        const item = placeholder.options[index];
        return item != undefined && item != null;
    } catch (error) {
        return false;
    }
}

export const store_dropdown_state = (placeholder: DropdownPlaceholder, new_index: number): void => {
    // Perform sanity checks on the index
    if (is_valid_index(placeholder, new_index)) {
        store_value(`${placeholder.name}_INDEX`, `${new_index}`);
        placeholder.current_value = placeholder.options[new_index].value;
        placeholder.current_index = new_index;
    } else {
        throw new Error(`Index must a whole number N, where 0 <= N < ${placeholder.options.length}. But it is ${new_index}`);
    }
}

export const load_dropdown_state = (placeholder: DropdownPlaceholder): void => {
    const stored_state = load_value(`${placeholder.name}_IS_CHECKED`);
    if (stored_state == null) {
        // No stored state -> use default value
        placeholder.current_index = placeholder.default_index;
    } else {
        const stored_index = Number(stored_state);
        if (is_valid_index(placeholder, stored_index)) {
            // Load the stored state
            placeholder.current_index = stored_index;
        } else {
            // Unexpected state, warn user and fall back to default
            console.warn(`Unexpected state for dropdown. Should be a whole number N, where 0 <= N < ${placeholder.options.length}. But it is ${stored_state}`);
            placeholder.current_index = placeholder.default_index;
        }
    }
    
    // Now we update the actual value based on the state
    placeholder.current_value = placeholder.options[placeholder.current_index].value;
}

// @TODO: resume here

PlaceholderPlugin.store_textbox_state = (placeholder_name, new_value) => {
    const is_validation_ok = PlaceholderPlugin.is_accepted_for_placeholder(new_value, placeholder_name);
    info(`Set textbox ${placeholder_name} to '${new_value}'. Validation ok? ${is_validation_ok}`);
    if (is_validation_ok) {
        localStorage.setItem(placeholder_name, new_value);
    } else {
        throw new Error(`Validation error: Value '${is_validation_ok}' is not valid for placeholder ${placeholder_name}`);
    }
}

PlaceholderPlugin.load_textbox_state = (placeholder_name) => {
    let value = localStorage.getItem(placeholder_name);
    if (!value) {
        value = PlaceholderPlugin.default_textbox_value(placeholder_name);
    }
    debug(`Read textbox ${placeholder_name}: '${value}'`);
    return value;
}

PlaceholderPlugin.default_textbox_value = (placeholder_name) => {
    let value = PlaceholderData.textbox_map[placeholder_name].value;
    if (value == undefined) {
        const value_fn = PlaceholderData.textbox_map[placeholder_name].value_function;
        try {
            // convert the result to string
            value = `${eval(value_fn)}`;
            debug(`Evaluating value_function: '${value_fn}' -> '${value}'`);
        } catch (error) {
            value = "EVALUATION_ERROR";
            console.error(`Error while evaluating value_function: '${value_fn}'\nError message: ${error}`);
        }
    }
    return value;
}

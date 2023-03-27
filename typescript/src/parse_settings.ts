import { load_checkbox_state, load_dropdown_state, load_textbox_state } from "./state_manager";
// This should be a more type safe reimplementation of 10_parse_data.js.
// It has some breaking changes, since I try to improve how the javascript code works

const assert_field_type = (name: string, expected_type_str: string, parent_object: any): any => {
    const value = parent_object[name];
    const actual_type_str = typeof(value);
    if (actual_type_str != expected_type_str) {
        throw new Error(`Type mismatch: ${name} should be ${expected_type_str}, but is ${actual_type_str}.\nProblematic object: ${JSON.stringify(parent_object)}`);
    } else {
        return value;
    }
}

// These functions are here to make sure, that I the type checker can properly work (since they have a specific return type)
const get_string_field = (name: string, parent_object: any): string => {
    return assert_field_type(name, "string", parent_object);
}

const get_boolean_field = (name: string, parent_object: any): boolean => {
    return assert_field_type(name, "boolean", parent_object);
}

const get_number_field = (name: string, parent_object: any): number => {
    return assert_field_type(name, "number", parent_object);
}

const get_array_field = (name: string, element_type: string, parent_object: any): any[] => {
    const array = parent_object[name];
    if (Array.isArray(array)) {
        for (const [index, entry] of array.entries()) {
            const actual_type_str = typeof(entry);
            if (actual_type_str != element_type) {
                const msg = `Type mismatch: ${name}'s ${index+1}th element should be ${element_type}, but is ${actual_type_str}.\nProblematic object: ${JSON.stringify(parent_object)}`;
                throw new Error(msg);
            }
        }
        return array;
    } else {
        throw new Error(`Type mismatch: ${name} should be an array, but is not.\nProblematic object: ${JSON.stringify(parent_object)}`);
    }
}

export interface PluginConfig {
    placeholders: Map<string,Placeholder>;
    textboxes: Map<string,TextboxPlaceholder>;
    checkboxes: Map<string,CheckboxPlaceholder>;
    dropdowns: Map<string,DropdownPlaceholder>;
    settings: PluginSettings,
}

export interface PluginSettings {
    debug: boolean;
    // apply_button: boolean;
    delay_millis: number;
    // reload_on_change: boolean; // To be maybe removed in the future
    // How normal placeholders are marked
    normal_prefix: string;
    normal_suffix: string;
    // How placeholders using the innerHTML method are marked
    html_prefix: string;
    html_suffix: string;
}

export interface BasePlaceholer {
    type: string;
    name: string;
    description: string;
    read_only: boolean;
    allow_inner_html: boolean;
    current_value: string;
    // How often it is used on the page. This does not necessarily need to be accurate, but 0 should always mean that it is not used on the page.
    count_on_page: number;
    // Whether a placeholder change can be done entirely dynamic, or whether it requires a complete reload of the page
    reload_page_on_change: boolean;
}

export interface TextboxPlaceholder extends BasePlaceholer {
    default_function?: () => string;
    default_value?: string;
    validators: string[];//TODO Validator type
}

export interface CheckboxPlaceholder extends BasePlaceholer {
    value_checked: string;
    value_unchecked: string;
    checked_by_default: boolean;
    current_is_checked: boolean;
}

export interface DropdownPlaceholder extends BasePlaceholer {
    options: DropdownOption[];
    default_index: number;
    current_index: number;
}

export interface DropdownOption {
    display_name: string;
    value: string;
}


export type Placeholder = TextboxPlaceholder | CheckboxPlaceholder | DropdownPlaceholder;

export const parse_config = (data: any): PluginConfig => {
    const placeholder_map: Map<string,Placeholder> = new Map<string,Placeholder>();
    const textboxes: Map<string,TextboxPlaceholder> = new Map<string,TextboxPlaceholder>();
    const checkboxes: Map<string,CheckboxPlaceholder> = new Map<string,CheckboxPlaceholder>();
    const dropdowns: Map<string,DropdownPlaceholder> = new Map<string,DropdownPlaceholder>();

    const placeholder_data = get_array_field("placeholder_list", "object", data);
    for (const pd of placeholder_data) {
        const placeholder = parse_any_placeholder(pd);

        // Add the placeholder to the correct lists
        placeholder_map.set(placeholder.name, placeholder);
        if (placeholder.type == "textbox") {
            textboxes.set(placeholder.name, placeholder as TextboxPlaceholder);
        } else if (placeholder.type == "checkbox") {
            checkboxes.set(placeholder.name, placeholder as CheckboxPlaceholder);
        } else if (placeholder.type == "dropdown") {
            dropdowns.set(placeholder.name, placeholder as DropdownPlaceholder);
        } else {
            console.warn("Unknown placeholder type:", placeholder.type);
        }
    }

    const settings_data = assert_field_type("settings", "object", data);
    return {
        "placeholders": placeholder_map,
        "textboxes": textboxes,
        "checkboxes": checkboxes,
        "dropdowns": dropdowns,
        "settings": parse_settings(settings_data),
    }
}

const parse_settings = (data: any): PluginSettings => {
    return {
        "debug": get_boolean_field("debug", data),
        "delay_millis": get_number_field("delay_millis", data),
        // How normal placeholders are marked
        "normal_prefix": "x",
        "normal_suffix": "x",
        // How placeholders using the innerHTML method are marked
        "html_prefix": "i",
        "html_suffix": "i",
        // @TODO resume here
    }
}


const parse_any_placeholder = (data: any): Placeholder => {
    const type = get_string_field("type", data);
    // Parse fields that are shared between all placeholders
    let parsed = {
        "type": type,
        "name": get_string_field("name", data),
        "description": get_string_field("description", data),
        "read_only": get_boolean_field("read_only", data),
        "allow_inner_html": get_boolean_field("allow_inner_html", data),
        "current_value": "UNINITIALIZED", // should be replaced by the 'load_*_state' funcion, that is called later on in this function
        "count_on_page": 0, // Will be incremented by the replace functions
        "reload_page_on_change": false, // May be changed by the replace function
    };

    // Parse the type specific attributes
    if (type === "textbox") {
        const placeholder = finish_parse_textbox(parsed, data);
        load_textbox_state(placeholder);
        return placeholder;
    } else if (type == "checkbox") {
        const placeholder = finish_parse_checkbox(parsed, data);
        load_checkbox_state(placeholder);
        return placeholder
    } else if (type == "dropdown") {
        const placeholder = finish_parse_dropdown(parsed, data);
        load_dropdown_state(placeholder);
        return placeholder;
    } else {
        throw new Error(`Unsupported placeholder type '${type}'`);
    }
}



const finish_parse_textbox = (parsed: BasePlaceholer, data: any): TextboxPlaceholder => {
    const validator_names = get_array_field("validators", "string", data);
    let default_function, default_value;
    if (data["default_value"] != undefined) {
        default_value = get_string_field("default_value", data);
    } else {
        const default_js_code = get_string_field("default_function", data);
        default_function = () => {
            // Wrap the function, so that we can ensure that errors are properly handled
            try {
                const result = eval(default_js_code);
                if (typeof(result) != "string") {
                    throw new Error(`Custom function '${default_js_code}' should return a string, but it returned a ${typeof(result)}: ${result}`);
                } else {
                    return result;
                }
            } catch (error) {
                throw new Error(`Failed to evaluate default_function '${default_js_code}' of placeholder ${parsed.name}: ${error}`);
            }
        }
    }
    return {
        "default_value": default_value,
        "default_function": default_function,
        validators: validator_names,
        ...parsed,
    }
}

const finish_parse_checkbox = (parsed: BasePlaceholer, data: any): CheckboxPlaceholder => {
    return {
        "value_checked": get_string_field("value_checked", data),
        "value_unchecked": get_string_field("value_unchecked", data),
        "checked_by_default": get_boolean_field("checked_by_default", data),
        "current_is_checked": false, // should be replaced by the 'load_*_state' function, that should be called on the result
        ...parsed,
    }
}

const finish_parse_dropdown = (parsed: BasePlaceholer, data: any): DropdownPlaceholder => {
    const raw_options = get_array_field("options", "object", data);
    const options: DropdownOption[] = [];
    for (const option of raw_options) {
        options.push({
            display_name: get_string_field("display_name", option),
            value: get_string_field("value", option),
        });
    }
    const default_index = get_number_field("default_index", data);
    if (default_index < 0) {
        throw new Error(`Invalid value: "default_index" should not be negative, but is ${default_index}.\nProblematic object: ${JSON.stringify(data)}`);
    } else if (default_index >= options.length) {
        throw new Error(`Invalid value: "default_index" should be smaller than the number of options (${options.length}), but is ${default_index}.\nProblematic object: ${JSON.stringify(data)}`);
    }
    return {
        "options": options,
        "default_index": default_index,
        "current_index": 0, // should be replaced by the 'load_*_state' function, that should be called on the result
        ...parsed,
    }
}


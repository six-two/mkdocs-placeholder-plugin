// This should be a more type safe reimplementation of 10_parse_data.js.
// It has some breaking changes, since I try to improve how the javascript code works

// do first level type checking (does not work for children of objects/lists)
const input_data = (window as any).PlaceholderPlugin.raw_data;

const assert_field_type = (name: string, expected_type_str: string, parent_object: any): any => {
    const value = parent_object[name];
    const actual_type_str = typeof(value);
    if (actual_type_str != expected_type_str) {
        const msg = `Type mismatch: ${name} should be ${expected_type_str}, but is ${actual_type_str}.\nProblematic object: ${JSON.stringify(parent_object)}`;
        throw new Error(msg);
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



export interface PluginSettings {
    debug: boolean;
    // apply_button: boolean;
    // delay_millis: number;
    // reload_on_change: boolean; // To be maybe removed in the future
    // placeholders: Map<string,Placeholder>;
    // textboxes: Map<string,Placeholder>;
}

export interface BasePlaceholer {
    type: string;
    description: string;
    read_only: boolean;
    allow_inner_html: boolean;
}

export interface TextboxPlaceholder extends BasePlaceholer {
    default_function: () => string;
    validators: string[];//TODO Validator type
}

export interface CheckboxPlaceholder extends BasePlaceholer {
    value_checked: string;
    value_unchecked: string;
    checked_by_default: boolean;
}

export type Placeholder = TextboxPlaceholder | CheckboxPlaceholder;

export const parse_settings = (data: any): PluginSettings => {
    return {
        "debug": get_boolean_field("debug", data),
        // @TODO resume here
    }
}

const parse_any_placeholder = (data: any): Placeholder => {
    const type = get_string_field("type", data);
    // Parse fields that are shared between all placeholders
    let parsed = {
        "type": type,
        "description": get_string_field("description", data),
        "read_only": get_boolean_field("read_only", data),
        "allow_inner_html": get_boolean_field("allow_inner_html", data),
    };

    // Parse the type specific attributes
    if (type === "textbox") {
        return finish_parse_textbox(parsed, data);
    } else if (type == "checkbox") {
        return finish_parse_checkbox(parsed, data);
        // @TODO: add dropdown too
    } else {
        throw new Error(`Unsupported placeholder type '${type}'`);
    }
}



const finish_parse_textbox = (parsed: BasePlaceholer, data: any): TextboxPlaceholder => {
    const validator_names = get_array_field("validators", "string", data);
    let default_fn;
    if (data["default_value"] != undefined) {
        const default_value = get_string_field("default_value", data);
        default_fn = () => default_value;
    } else {
        const default_js_code = get_string_field("default_function", data);
        default_fn = () => {
            // Wrap the function, so that we can ensure that errors are properly handled
            try {
                const result = eval(default_js_code);
                if (typeof(result) != "string") {
                    throw new Error(`Custom function '${default_js_code}' should return a string, but it returned a ${typeof(result)}: ${result}`);
                } else {
                    return result;
                }
            } catch (error) {
                throw new Error(`Failed to evaluate custom code '${default_js_code}': ${error}`);
            }
        }
    }
    return {
        "default_function": default_fn,
        validators: validator_names,
        ...parsed,
    }
}

const finish_parse_checkbox = (parsed: BasePlaceholer, data: any): CheckboxPlaceholder => {
    return {
        "value_checked": get_string_field("value_checked", data),
        "value_unchecked": get_string_field("value_unchecked", data),
        "checked_by_default": get_boolean_field("checked_by_default", data),    
        ...parsed,
    }
}


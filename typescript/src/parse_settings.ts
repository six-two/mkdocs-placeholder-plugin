import { load_checkbox_state, load_dropdown_state, load_textbox_state, load_boolean_setting } from "./state_manager";
import { InputValidator, parse_validator } from "./validator";
import { DependencyGraph } from "./dependency_graph";

// It parses random unspecified data, so any should be fine
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const assert_field_type = (name: string, expected_type_str: string, parent_object: any): any => {
    const value = parent_object[name];
    const actual_type_str = typeof(value);
    if (actual_type_str != expected_type_str) {
        throw new Error(`Type mismatch: ${name} should be ${expected_type_str}, but is ${actual_type_str}.\nProblematic object: ${JSON.stringify(parent_object)}`);
    } else {
        return value;
    }
}

// These functions are here to make sure, that I the type checker can properly work (since they have a specific return type)

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const get_string_field = (name: string, parent_object: any): string => {
    return assert_field_type(name, "string", parent_object);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const get_boolean_field = (name: string, parent_object: any): boolean => {
    return assert_field_type(name, "boolean", parent_object);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const get_number_field = (name: string, parent_object: any): number => {
    return assert_field_type(name, "number", parent_object);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const get_array_field = (name: string, element_type: string, parent_object: any): any[] => {
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
    settings: PluginSettings;
    dependency_graph: DependencyGraph;
    // used by the inline editor event listeners. Enables removing them all at once
    event_listener_abort_controller: AbortController;
    input_tables: InputTable[];
}

export interface InputTable {
    table_element: HTMLElement;
    columns: string[];
    rows: InputTableRow[];
}

export interface InputTableRow {
    element: HTMLElement;
    placeholder: Placeholder;
}

export interface PluginSettings {
    debug: boolean;
    delay_millis: number;
    apply_change_on_focus_change: boolean;
    expand_auto_tables: boolean;
    highlight_placeholders: boolean;
    inline_editors: boolean;
    inline_editor_icons: boolean;
    normal_is_alias_for: string;

    // How different placeholder types are marked
    normal_prefix: string;
    normal_suffix: string;
    editable_prefix: string;
    editable_suffix: string;
    html_prefix: string;
    html_suffix: string;
    static_prefix: string;
    static_suffix: string;
    dynamic_prefix: string;
    dynamic_suffix: string;
}

export interface BasePlaceholer {
    name: string;
    description: string;
    read_only: boolean;
    allow_inner_html: boolean;
    // used for sorting placeholders
    order_index: number;
    // Regexes for finding placeholder in page
    regex_dynamic: RegExp;
    regex_editable: RegExp;
    regex_html: RegExp;
    regex_normal: RegExp;
    regex_static: RegExp;
    // Elements on the page to update if the value changes
    output_elements: HTMLElement[];
    // The tooltip that will be shown when the placeholder is not currently edited
    default_tooltip: string;

    // Allow replacing placeholders within the value of this
    allow_nested: boolean;
    // the value as it is stored (with placeholders in the value not replaced)
    current_value: string;
    // the value after any placeholders it contains are recursively replaced (if allow_nested is true)
    expanded_value: string;
    // How often it is used on the page. This does not necessarily need to be accurate, but 0 should always mean that it is not used on the page.
    count_on_page: number;
    // Whether a placeholder change can be done entirely dynamic, or whether it requires a complete reload of the page
    reload_page_on_change: boolean;
    // The input elements for this placeholder
}

export interface TextboxPlaceholder extends BasePlaceholer {
    type: InputType;
    default_function?: () => string;
    default_value?: string;
    validators: InputValidator[];
    input_elements: HTMLInputElement[];
}

export interface CheckboxPlaceholder extends BasePlaceholer {
    type: InputType
    value_checked: string;
    value_unchecked: string;
    checked_by_default: boolean;
    current_is_checked: boolean;
    input_elements: HTMLInputElement[];
}

export interface DropdownPlaceholder extends BasePlaceholer {
    type: InputType;
    options: DropdownOption[];
    default_index: number;
    current_index: number;
    input_elements: HTMLSelectElement[];
}

export interface DropdownOption {
    display_name: string;
    value: string;
}

export enum ReplaceType {
    // Excluding normal, since it is just an alias for one of the other types
    Editable = "editable",

}

export enum InputType {
    Textbox = "TEXTBOX",
    Checkbox = "CHECKBOX",
    Dropdown = "DROPDOWN",
}

export type Placeholder = TextboxPlaceholder | CheckboxPlaceholder | DropdownPlaceholder;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const parse_config = (data: any): PluginConfig => {
    const placeholder_map: Map<string,Placeholder> = new Map<string,Placeholder>();
    const textboxes: Map<string,TextboxPlaceholder> = new Map<string,TextboxPlaceholder>();
    const checkboxes: Map<string,CheckboxPlaceholder> = new Map<string,CheckboxPlaceholder>();
    const dropdowns: Map<string,DropdownPlaceholder> = new Map<string,DropdownPlaceholder>();

    const validator_map = new Map<string,InputValidator>();
    const validator_data_list = get_array_field("validators", "object", data);
    for (const validator_data of validator_data_list) {
        const validator = parse_validator(validator_data);
        if (validator_map.has(validator.id)) {
            throw new Error(`Multiple validators with id '${validator.id}'`);
        } else {
            validator_map.set(validator.id, validator);
        }
    }

    const settings_data = assert_field_type("settings", "object", data);
    const settings = parse_settings(settings_data);

    const placeholder_data = get_array_field("placeholder_list", "object", data);
    for (let i = 0; i < placeholder_data.length; i++) {
        const placeholder = parse_any_placeholder(placeholder_data[i], validator_map, settings, i);

        // Add the placeholder to the correct lists
        placeholder_map.set(placeholder.name, placeholder);
        if (placeholder.type == InputType.Textbox) {
            textboxes.set(placeholder.name, placeholder as TextboxPlaceholder);
        } else if (placeholder.type == InputType.Checkbox) {
            checkboxes.set(placeholder.name, placeholder as CheckboxPlaceholder);
        } else if (placeholder.type == InputType.Dropdown) {
            dropdowns.set(placeholder.name, placeholder as DropdownPlaceholder);
        } else {
            console.warn("Unknown placeholder type:", placeholder.type);
        }
    }

    const graph = new DependencyGraph(placeholder_map);

    return {
        "placeholders": placeholder_map,
        "textboxes": textboxes,
        "checkboxes": checkboxes,
        "dropdowns": dropdowns,
        "settings": settings,
        "dependency_graph": graph,
        "input_tables": [],
        "event_listener_abort_controller": new AbortController(),
    }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const parse_settings = (data: any): PluginSettings => {
    const apply_change_on_focus_change_default = get_boolean_field("apply_change_on_focus_change", data);
    const debug_default = get_boolean_field("debug", data);
    const expand_auto_tables_default = get_boolean_field("expand_auto_tables", data);
    const inline_editors = get_boolean_field("inline_editors", data);
    const inline_editor_icons = get_boolean_field("inline_editor_icons", data);
    
    return {
        "apply_change_on_focus_change": load_boolean_setting("apply_change_on_focus_change", apply_change_on_focus_change_default),
        "debug": load_boolean_setting("debug", debug_default),
        "delay_millis": get_number_field("delay_millis", data),
        "expand_auto_tables": load_boolean_setting("expand_auto_tables", expand_auto_tables_default),
        "highlight_placeholders": load_boolean_setting("highlight_placeholders", false),
        "inline_editors": load_boolean_setting("inline_editors", inline_editors),
        "inline_editor_icons": load_boolean_setting("inline_editor_icons", inline_editor_icons),
        "normal_is_alias_for": get_string_field("normal_is_alias_for", data),
        // How normal placeholders are marked
        "normal_prefix": get_string_field("normal_prefix", data),
        "normal_suffix": get_string_field("normal_suffix", data),
        // How editable placeholders are marked
        "editable_prefix": get_string_field("editable_prefix", data),
        "editable_suffix": get_string_field("editable_suffix", data),
        // How placeholders using the innerHTML method are marked
        "html_prefix": get_string_field("html_prefix", data),
        "html_suffix": get_string_field("html_suffix", data),
        // How placeholders using the direct/static replacement methodare marked
        "static_prefix": get_string_field("static_prefix", data),
        "static_suffix": get_string_field("static_suffix", data),
        // How placeholders using the dynamic replacement methodare marked
        "dynamic_prefix": get_string_field("dynamic_prefix", data),
        "dynamic_suffix": get_string_field("dynamic_suffix", data),
    }
}

const escapeRegExp = (regex_pattern: string) => {
    // @SOURCE https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions#escaping
    return regex_pattern.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); // $& means the whole matched string
  }


// eslint-disable-next-line @typescript-eslint/no-explicit-any
const parse_any_placeholder = (data: any, validator_map: Map<string,InputValidator>, settings: PluginSettings, index: number): Placeholder => {
    const type = get_string_field("type", data);
    // Parse fields that are shared between all placeholders
    const name = get_string_field("name", data);
    const parsed = {
        "name": name,
        "order_index": index,
        // The regexes for the different replace methods. Stored here so that I only need to compile them once

        // @TODO: editable
        "regex_dynamic": RegExp(escapeRegExp(settings.dynamic_prefix) + name + escapeRegExp(settings.dynamic_suffix), "g"),
        "regex_editable": RegExp(escapeRegExp(settings.editable_prefix) + name + escapeRegExp(settings.editable_suffix), "g"),
        "regex_html": RegExp(escapeRegExp(settings.html_prefix) + name + escapeRegExp(settings.html_suffix), "g"),
        "regex_normal": RegExp(escapeRegExp(settings.normal_prefix) + name + escapeRegExp(settings.normal_suffix), "g"),
        "regex_static": RegExp(escapeRegExp(settings.static_prefix) + name + escapeRegExp(settings.static_suffix), "g"),
        // 
        "default_tooltip": "", // have it empty by default, the different finish_parse_<type> functions will overwrite it if needed
        "description": get_string_field("description", data),
        "read_only": get_boolean_field("read_only", data),
        "allow_inner_html": get_boolean_field("allow_inner_html", data),
        "allow_nested": get_boolean_field("allow_nested", data),
        "current_value": "UNINITIALIZED", // should be replaced by the 'load_*_state' funcion, that is called later on in this function
        "expanded_value": "UNINITIALIZED", // should be replaced by the 'load_*_state' funcion, that is called later on in this function
        "count_on_page": 0, // Will be incremented by the replace functions
        "reload_page_on_change": false, // May be changed by the replace function
        "output_elements": [], // Will be set, when the page is searched
    };

    // Parse the type specific attributes
    if (type === "textbox") {
        const placeholder = finish_parse_textbox(parsed, data, validator_map);
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


// eslint-disable-next-line @typescript-eslint/no-explicit-any
const finish_parse_textbox = (parsed: BasePlaceholer, data: any, validator_map: Map<string,InputValidator>): TextboxPlaceholder => {
    let default_function, default_value;
    if (data["default_value"] != undefined) {
        default_value = get_string_field("default_value", data);
    } else {
        const default_js_code = get_string_field("default_function", data);
        default_function = () => {
            // Wrap the function, so that we can ensure that errors are properly handled
            try {
                const compiled_function = new Function(default_js_code);
                const result = compiled_function();
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

    const validator_names: string[] = get_array_field("validators", "string", data);
    const validator_list: InputValidator[] = [];
    for (const name of validator_names) {
        const validator = validator_map.get(name);
        if (validator) {
            validator_list.push(validator);
        } else {
            const known_validators = Array.from(validator_map.keys()).join(", ");
            throw new Error(`No validator with id '${name}' was found. Known validators are ${known_validators}`);
        }
    }

    const description = parsed.description ? `\nDescription: ${parsed.description}` : "";
    const default_value_line = default_value ? `\nDefault value: ${default_value}` : `\nDefault value generated by function`;
    const validation_ok_tooltip = `Placeholder name: ${parsed.name}${description}${default_value_line}\nUsage: Click to edit the value. Leaving the text field or pressing enter will store the new value, pressing Escape will revert current changes. While editing the field, the tooltip will show warnings/errors if your value is not what is expected`;

    return {
        ...parsed,
        "default_tooltip": validation_ok_tooltip,
        "default_function": default_function,
        "default_value": default_value,
        "input_elements": [],
        "type": InputType.Textbox,
        "validators": validator_list,
    }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const finish_parse_checkbox = (parsed: BasePlaceholer, data: any): CheckboxPlaceholder => {
    return {
        ...parsed,
        "checked_by_default": get_boolean_field("checked_by_default", data),
        "current_is_checked": false, // should be replaced by the 'load_*_state' function, that should be called on the result
        "input_elements": [],
        "value_checked": get_string_field("value_checked", data),
        "value_unchecked": get_string_field("value_unchecked", data),
        "type": InputType.Checkbox,
    }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
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

    const description = parsed.description ? `\nDescription: ${parsed.description}` : "";
    let default_tooltip = `Placeholder name: ${parsed.name}${description}\nDefault option: ${options[default_index].value}\nUsage: (left-)click to cycle forward through the values, right-click to cycle through backwards. You can also use the Enter, Up, and Down keys if the placeholder is selected.\nPossible values:`;

    for (const option of options) {
        default_tooltip += `\n- ${option.value}`;
    }

    return {
        ...parsed,
        "default_tooltip": default_tooltip,
        "current_index": 0, // should be replaced by the 'load_*_state' function, that should be called on the result
        "default_index": default_index,
        "input_elements": [],
        "options": options,
        "type": InputType.Dropdown,
    }
}



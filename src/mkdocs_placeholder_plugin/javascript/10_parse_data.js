// do first level type checking (does not work for children of objects/lists)
const assert_field_type = (name, expected_type_str, parent_object = PlaceholderPlugin.raw_data) => {
    const value = parent_object[name];
    const actual_type_str = typeof(value);
    if (actual_type_str != expected_type_str) {
        const msg = `Type mismatch: ${name} should be ${expected_type_str}, but is ${actual_type_str}`;
        throw new Error(msg);
    } else {
        return value;
    }
}

// We store it in a special variable for easier inspection/referencing
const PlaceholderData = {
    "debug": assert_field_type("debug", "boolean"),
    "fix_style": true,// @TODO: get from plugin's config
    "delay_millis": assert_field_type("delay_millis", "number"),
    "reload": assert_field_type("reload", "boolean"),
    // name:str -> { "value" -> default_value:str, "read_only" -> bool }
    "textbox_map": assert_field_type("textbox", "object"),
    // name:str -> { "checked" -> value:str, "unchecked" -> value:str, "default_value" -> checked_by_default:bool, "read_only" -> bool }
    "checkbox_map": assert_field_type("checkbox", "object"),
    // name:str -> { "default_index" -> default:int, "options" -> list of [display_name:str, actual_value:str], "read_only" -> bool }
    "dropdown_map": assert_field_type("dropdown", "object"),
    // name:str -> description:str
    "description_map": assert_field_type("descriptions", "object"),
}
// Derive some helpful fields
PlaceholderData.names = Object.keys(PlaceholderData.description_map);
// TODO: pass readonly, and other settings (auto reload, etc) to this script too


// Check textbox field in depth
for (textbox of Object.values(PlaceholderData.textbox_map)) {
    assert_field_type("value", "string", textbox);
    assert_field_type("read_only", "boolean", textbox);
}

// Check textbox field in depth
for (checkbox of Object.values(PlaceholderData.checkbox_map)) {
    // The value to use if the checkbox is checked
    assert_field_type("checked", "string", checkbox);
    // The value to use if the checkbox is unchecked
    assert_field_type("unchecked", "string", checkbox);
    
    assert_field_type("default_value", "boolean", checkbox);
    assert_field_type("read_only", "boolean", checkbox);
}

// Check dropdown field in depth
for (dropdown of Object.values(PlaceholderData.dropdown_map)) {
    // options: array (object) of array (object) of strings
    assert_field_type("options", "object", dropdown);
    for (option of dropdown.options) {
        if (typeof(option) == "object") {
            if (option.length != 2) {
                throw new Error(`Expected 2 list items, but received ${option.length}`);
            }
            if (typeof(option[0]) != "string") {
                throw new Error(`Display name is ${typeof(option[0])}, but should be string`);
            }
            if (typeof(option[1]) != "string") {
                throw new Error(`Value is ${typeof(option[1])}, but should be string`);
            }
        }
    }

    assert_field_type("default_index", "number", dropdown);
    assert_field_type("read_only", "boolean", dropdown);
}


// Set up or disable logging as early as possible
let log, info, debug;
if (PlaceholderData.debug) {
    // Write debugging messages to console
    debug = console.debug;
    info = console.info;
    log = console.log;
} else {
    // If debugging is disabled, make the functions do nothing
    debug = () => {};
    info = () => {};
    log = () => {};
}

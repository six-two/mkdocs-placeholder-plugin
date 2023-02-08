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
    "delay_millis": assert_field_type("delay_millis", "number"),
    "reload": assert_field_type("reload", "boolean"),
    // name:str -> { "value" -> default_value:str, "read_only" -> bool }
    "textbox_map": assert_field_type("textbox", "object"),
}

// Check textbox field in depth
for (textbox of Object.values(PlaceholderData.textbox_map)) {
    assert_field_type("value", "string", textbox);
    assert_field_type("read_only", "boolean", textbox)
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

// do first level type checking (does not work for children of objects/lists)
const assert_field_type = (name, expected_type_str, parent_object = PlaceholderPlugin.raw_data) => {
    const value = parent_object[name];
    const actual_type_str = typeof(value);
    if (actual_type_str != expected_type_str) {
        const msg = `Type mismatch: ${name} should be ${expected_type_str}, but is ${actual_type_str}.\nProblematic object: ${JSON.stringify(parent_object)}`;
        throw new Error(msg);
    } else {
        return value;
    }
}

// We store it in a special variable for easier inspection/referencing
const PlaceholderData = {
    "debug": assert_field_type("debug", "boolean"),
    "fix_style": true,// @TODO: get from plugin's config
    "auto_table_hide_read_only": assert_field_type("auto_table_hide_read_only", "boolean"),
    "auto_table_apply_button": assert_field_type("auto_table_apply_button", "boolean"),
    "custom_css": assert_field_type("custom_css", "string"),
    "delay_millis": assert_field_type("delay_millis", "number"),
    "reload": assert_field_type("reload", "boolean"),
    // name:str -> { "value" -> default_value:str }
    "textbox_map": assert_field_type("textbox", "object"),
    // name:str -> { "checked" -> value:str, "unchecked" -> value:str, "default_value" -> checked_by_default:bool }
    "checkbox_map": assert_field_type("checkbox", "object"),
    // name:str -> { "default_index" -> default:int, "options" -> list of [display_name:str, actual_value:str] }
    "dropdown_map": assert_field_type("dropdown", "object"),
    // name:str -> { "description" -> str, "read_only" -> bool, "replace_everywhere" -> bool }
    "common_map": assert_field_type("common", "object"),
}
// Derive some helpful fields
PlaceholderData.names = Object.keys(PlaceholderData.common_map);


// Check textbox field in depth
for (const textbox of Object.values(PlaceholderData.textbox_map)) {
    // either value_function or value should be defined
    if (textbox.value == undefined) {
        assert_field_type("value_function", "string", textbox);
    } else {
        assert_field_type("value", "string", textbox);
    }

    // Check validators
    if (textbox.validators != undefined) {
        assert_field_type("validators", "object", textbox);
        for (const validator of textbox.validators) {
            assert_field_type("name", "string", validator);
            assert_field_type("rules", "object", validator);
            for (const rule of validator.rules) {
                assert_field_type("severity", "string", rule);
                if (rule.regex) {
                    assert_field_type("regex", "string", rule);
                    // Compile the regex for better performance
                    rule.regex = new RegExp(rule.regex);
                } else {
                    assert_field_type("match_function", "string", rule);
                }
                assert_field_type("should_match", "boolean", rule);
                assert_field_type("error_message", "string", rule);
            }
        }
    }
}

// Check textbox field in depth
for (const checkbox of Object.values(PlaceholderData.checkbox_map)) {
    // The value to use if the checkbox is checked
    assert_field_type("checked", "string", checkbox);
    // The value to use if the checkbox is unchecked
    assert_field_type("unchecked", "string", checkbox);

    assert_field_type("default_value", "boolean", checkbox);
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
}

// Check attributes set for all placeholders (independent of type) in depth
for (common of Object.values(PlaceholderData.common_map)) {
    assert_field_type("description", "string", common);
    assert_field_type("read_only", "boolean", common);
    assert_field_type("replace_everywhere", "boolean", common);
}

PlaceholderPlugin.validate_input = (value, placeholder_name) => {
    const messages = [];
    const validator_list = PlaceholderData.textbox_map[placeholder_name].validators;
    if (validator_list) {
        for (const validator of validator_list) {
            const new_messages = PlaceholderPlugin.get_validator_error_messages(value, validator);
            if (new_messages.length == 0) {
                // This validator passes without errors -> everything is ok
                if (validator_list.length == 1) {
                    return ["ok", `Expecting: ${validator.name}`];
                } else {
                    const lines = ["Expecting one of the following:"];
                    for (const v of validator_list) {
                        lines.push(` - ${v.name}`);
                    }
                    return ["ok", lines.join("\n")];
                }
            } else {
                messages.push(new_messages);
            }
        }

        // @TODO: can I somehow simplify the following mess?
        // none of the validators returned ok.
        let all_have_errors = true;
        for (const message_list of messages) {
            let has_errors = false;
            for (const message of message_list) {
                if (message[0] == "error") {
                    has_errors = true;
                }
            }
            if (!has_errors) {
                all_have_errors = false;
            }
        }
        const filtered_messages = [];
        if (all_have_errors) {
            // If all of them have errors, we will remove the warnings to keep it shorter
            for (const message_list of messages) {
                for (const message of message_list) {
                    if (message[0] == "error") {
                        filtered_messages.push(message[1]);
                    }
                }
            }
            return ["error", filtered_messages.join("\n")];
        } else {
            // If some return warnings and some return errors, we will only show the ones with warnings.
            for (const message_list of messages) {
                let this_has_error = false;
                for (const message of message_list) {
                    if (message[0] == "error") {
                        this_has_error = true;
                    }
                }
                if (!this_has_error) {
                    filtered_messages.push(...(message_list.map(x => x[1])));
                }
            }
            return ["warn", filtered_messages.join("\n")];
        }
    }
    return [];
}

PlaceholderPlugin.get_validator_error_messages = (value, validator) => {
    const messages = [];
    for (const rule of validator.rules) {
        const is_match = rule.regex.test(value);
        if (is_match != rule.should_match) {
            messages.push([rule.severity, `[${validator.name}] ${rule.error_message}`]);
        }
    }
    return messages;
}

PlaceholderPlugin.remove_tooltip = (input_field) => {
    // Remove highlighting
    input_field.classList.remove("validation-error", "validation-warn", "validation-ok");

    // Remove tooltip
    input_field.title = "";
}

PlaceholderPlugin.show_tooltip = (input_field, rating, message) => {
    // Set highlighting
    input_field.classList.remove("validation-error", "validation-warn", "validation-ok");
    input_field.classList.add(`validation-${rating}`);

    // Set tooltip
    input_field.title = message;
}

// apply_value: if set to true, this value will be set if it passes muster, otherwise a popup will be shown
// @TODO later: performance improvements: cache regex, only apply to fields that actually have validators set
PlaceholderPlugin.validate_input_field = (input_field, placeholder_name, apply_value) => {
    const status = PlaceholderPlugin.validate_input(input_field.value, placeholder_name);
    debug("Validation:", placeholder_name, input_field.value, status);
    if (status && status.length != 0) {
        const [rating, message] = status;

        PlaceholderPlugin.show_tooltip(input_field, rating, message);

        if (rating == "error" && apply_value) {
            alert(`Failed to apply value for placeholder ${placeholder_name} because it does not pass validation.\n${message}`);
            return;
        }
    } else {
        PlaceholderPlugin.remove_tooltip(input_field);
    }

    if (apply_value) {
        PlaceholderPlugin.store_textbox_state(placeholder_name, input_field.value);
        PlaceholderPlugin.on_placeholder_change();
    }
}

PlaceholderPlugin.validate_input = (value, placeholder_name) => {
    const data = PlaceholderData.textbox_map[placeholder_name];
    if (data) {
        const must_match = data["must_match"]
        if (must_match) {
            const regex = new RegExp(must_match.regex);
            if (!regex.test(value)) {
                return ["error", must_match.message];
            }
        }
        const should_match = data["should_match"]
        if (should_match) {
            const regex = new RegExp(should_match.regex);
            if (!regex.test(value)) {
                return ["warn", should_match.message];
            }
        }
    }
    return null;
}

PlaceholderPlugin.remove_tooltip = (input_field) => {
    input_field.classList.remove("validation-error", "validation-warn");
    // TODO
}

PlaceholderPlugin.show_tooltip = (input_field, rating, message) => {
    input_field.classList.remove("validation-error", "validation-warn");
    input_field.classList.add(`validation-${rating}`);
    // TODO
}

// apply_value: if set to true, this value will be set if it passes muster, otherwise a popup will be shown
// @TODO later: performance improvements: cache regex, only apply to fields that actually have validators set
PlaceholderPlugin.validate_input_field = (input_field, placeholder_name, apply_value) => {
    const status = PlaceholderPlugin.validate_input(input_field.value, placeholder_name);
    debug("Validation:", placeholder_name, input_field.value, status);
    if (status) {
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

import { logger } from "./debug";
import { get_array_field, get_boolean_field, get_string_field, TextboxPlaceholder } from "./parse_settings";

export interface InputValidator {
    display_name: string;
    id: string;
    rules: ValidatorRule[];
}

export interface ValidatorRule {
    severity: ValidatorSeverity;
    is_match_function: (value: string) => boolean;
    should_match: boolean;
    error_message: string;
}

export enum ValidatorSeverity {
    Warning = "WARNING",
    Error = "ERROR",
}

export enum PlaceholderValidatity {
    Good = "GOOD",
    Warning = "WARNING",
    Error = "ERROR",
    NoValidator = "NO_VALIDATOR",
}


interface ValidatorResult {
    warnings: string[];
    errors: string[];
}

export interface PlaceholderValidatorResult {
    rating: PlaceholderValidatity,
    message: string,
}

export const parse_validator = (data: any): InputValidator => {
    const rules = get_array_field("rules", "object", data);
    if (rules.length == 0) {
        throw new Error(`Rules should not be an empty array.\nProblematic object: ${JSON.stringify(data)}`);
    }
    const id = get_string_field("id", data);
    return {
        "display_name": get_string_field("display_name", data),
        "id": id,
        "rules": rules.map(x => parse_rule(x, id)),
    }
}

const is_valid_value = (validator: InputValidator, value: string): boolean => {
    for (const rule of validator.rules) {
        if (rule.is_match_function(value) != rule.should_match) {
            // this rule rejects the value
            if (rule.severity == ValidatorSeverity.Error) {
                // immediately return once we found a hard failure
                return false;
            }
        }
    }
    // no real errors -> is valid
    return true;
}

export const is_valid_value_for_placeholder = (placeholder: TextboxPlaceholder, value: string) => {
    if (placeholder.validators.length > 0) {
        for (const validator of placeholder.validators) {
            if (is_valid_value(validator, value)) {
                // a single validator accepting it is enough
                return true;
            }
        }
        // no validator accepted it -> bad
        return false;
    } else {
        return true;
    }
}


const validate_value = (validator: InputValidator, value: string): ValidatorResult => {
    const warnings = []
    const errors = []
    for (const rule of validator.rules) {
        if (rule.is_match_function(value) != rule.should_match) {
            // this rule rejects the value
            if (rule.severity == ValidatorSeverity.Error) {
                errors.push(`[${validator.display_name}] Error: ${rule.error_message}`);
            } else if (rule.severity == ValidatorSeverity.Warning) {
                warnings.push(`[${validator.display_name}] Warning: ${rule.error_message}`);
            } else {
                console.warn(`Unknown rule severity ${rule.severity}`);
            }
        }
    }
    return {
        "errors": errors,
        "warnings": warnings,
    }
}

const validate_placeholder_value = (placeholder: TextboxPlaceholder, value: string): PlaceholderValidatorResult => {
    const result_list = [];
    let has_no_error = false; // whether at least one placeholder has no errors
    if (placeholder.validators.length > 0) {
        for (const validator of placeholder.validators) {
            const result = validate_value(validator, value);
            result_list.push(result);

            if (result.errors.length == 0) {
                has_no_error = true;
                if (result.warnings.length == 0) {
                    return placeholder_is_good(placeholder);
                }
            }
        }

        if (has_no_error) {
            return placeholder_is_warning(result_list);
        } else {
            return placeholder_is_error(result_list);
        }
    } else {
        return {
            "rating": PlaceholderValidatity.NoValidator,
            "message": "No validators are specified for this placeholder",
        }
    }
}

const placeholder_is_error = (result_list: ValidatorResult[]): PlaceholderValidatorResult => {
    // If all of them have errors, we will ignore the warnings to keep it shorter
    const errors = [];
    for (const result of result_list) {
        errors.push(...result.errors);
    }
    return {
        "rating": PlaceholderValidatity.Error,
        "message": errors.join("\n"),
    }
}

const placeholder_is_warning = (result_list: ValidatorResult[]): PlaceholderValidatorResult => {
    // If some return warnings and some return errors, we will only show the ones with warnings.
    const lines = [];
    for (const result of result_list) {
        if (result.errors.length == 0) {
            lines.push(...result.warnings);
        }
    }
    return {
        "rating": PlaceholderValidatity.Warning,
        "message": lines.join("\n"),
    }
}

const placeholder_is_good = (placeholder: TextboxPlaceholder): PlaceholderValidatorResult => {
    // If one of them has neither warnings or errors, we return Good status immediately
    let message;
    if (placeholder.validators.length == 1) {
        message = `Expecting: ${placeholder.validators[0].display_name}`;
    } else {
        message = "Expecting one of the following: ";
        for (const v of placeholder.validators) {
            message += `\n - ${v.display_name}`;
        }
    }
    return {
        "rating": PlaceholderValidatity.Good,
        "message": message,
    };
}



const parse_rule = (data: any, validator_id: string): ValidatorRule => {
    const severity_str = get_string_field("severity", data);
    let severity;
    if (severity_str == "warning" || severity_str == "warn") {
        severity = ValidatorSeverity.Warning;
    } else if (severity_str == "error") {
        severity = ValidatorSeverity.Error;
    } else {
        throw new Error(`Unknown severity '${severity_str}'`);
    }
    let is_match_function;
    if ((data as any).regex) {
        const regex = get_string_field("regex", data);
        const compiled_regex = new RegExp(regex);
        is_match_function = (value: string) => compiled_regex.test(value);
    } else {
        const match_function_body = get_string_field("match_function", data);
        // we need to use Function instead of eval(), since minification will rename the argument
        // this may also be more performant, since the code is only compiled once
        const match_function = new Function("value", match_function_body);
        is_match_function = (value: string): boolean => {
            try {
                const result = match_function(value);
                if (typeof(result) != "boolean") {
                    throw new Error(`Custom match_function '${match_function_body}' of validator ${validator_id} should return a boolean, but it returned a ${typeof(result)}: ${result}`);
                } else {
                    return result;
                }
            } catch (error) {
                throw new Error(`Failed to evaluate match_function '${match_function_body}' of validator ${validator_id}: ${error}`);
            }
        };
    }
    return {
        "severity": severity,
        "should_match": get_boolean_field("should_match", data),
        "error_message": get_string_field("error_message", data),
        "is_match_function": is_match_function,
    }
}


const update_tooltip = (input_field: HTMLInputElement, validation_result: PlaceholderValidatorResult): void => {
    // Set highlighting
    input_field.classList.remove("validation-error", "validation-warn", "validation-ok", "validation-none");
    if (validation_result.rating == PlaceholderValidatity.Good) {
        input_field.classList.add(`validation-ok`);
    } else if (validation_result.rating == PlaceholderValidatity.Warning) {
        input_field.classList.add(`validation-warn`);
    } else if (validation_result.rating == PlaceholderValidatity.Error) {
        input_field.classList.add(`validation-error`);
    } else if (validation_result.rating == PlaceholderValidatity.NoValidator) {
        input_field.classList.add(`validation-none`);
    } else {
        console.warn(`Unknown placeholder validity: ${validation_result.rating}`);
    }

    // Set tooltip
    input_field.title = validation_result.message;
}

// Returns "false" if the value has an error, so for example page reloading should be cancelled.
export const validate_textbox_input_field = (placeholder: TextboxPlaceholder, input_field: HTMLInputElement) => {
    const result = validate_placeholder_value(placeholder, input_field.value);
    update_tooltip(input_field, result);

    logger.debug("Validation: name =", placeholder.name, ", value =", input_field.value, ", results =", result.rating);

    const can_accept_value = result.rating != PlaceholderValidatity.Error;
    return can_accept_value;
}

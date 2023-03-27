import { get_array_field, get_boolean_field, get_string_field } from "./parse_settings";

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

export interface ValidatorResult {
    warnings: string[];
    errors: string[];
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

const parse_rule = (data: any, validator_id: string): ValidatorRule => {
    const severity_str = get_string_field("severity", data);
    let severity;
    if (severity_str == "warning") {
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


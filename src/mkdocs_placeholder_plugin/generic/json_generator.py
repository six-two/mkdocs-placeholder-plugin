import json
# local
from . import PlaceholderConfigError
from .config import Placeholder, InputType, PlaceholderConfig, Validator, ValidatorRule, PlaceholderSettings

def generate_json_for_javascript_code(config: PlaceholderConfig) -> str:
    """
    Generate the JSON string, that will replace the placeholder in the JavaScript file
    """
    placeholder_data_list = [placeholder_to_serializable_dict(x) for x in config.placeholders.values()]
    validator_data_list = [validator_to_dict(x) for x in config.validators.values() if x.is_used()]
    settings_data = settings_to_serializable_dict(config.settings)

    result_object = {
        "placeholder_list": placeholder_data_list,
        "settings": settings_data,
        "validators": validator_data_list,
    }
    return json.dumps(result_object, indent=None, sort_keys=False)


def settings_to_serializable_dict(settings: PlaceholderSettings) -> dict:
    return {
        "debug": settings.debug_javascript,
        "delay_millis": settings.replace_delay_millis,
        "dynamic_prefix": settings.dynamic_prefix,
        "dynamic_suffix": settings.dynamic_suffix,
        "normal_prefix": settings.normal_prefix,
        "normal_suffix": settings.normal_suffix,
    }

def placeholder_to_serializable_dict(placeholder: Placeholder) -> dict:
    placeholder_data = {
        "name": placeholder.name,
        "description": placeholder.description,
        "read_only": placeholder.read_only,
        "allow_inner_html": placeholder.replace_everywhere,
        "allow_nested": placeholder.allow_nested,
    }
    if placeholder.input_type == InputType.Checkbox:
        placeholder_data.update({
            "type": "checkbox",
            "value_checked": placeholder.values["checked"],
            "value_unchecked": placeholder.values["unchecked"],
            "checked_by_default": bool(placeholder.default_value == "checked"),
        })
    elif placeholder.input_type == InputType.Dropdown:
        # Figure out the index of the item selected by default
        default_index = 0
        for index, value in enumerate(placeholder.values.keys()):
            if placeholder.default_value == value:
                default_index = index

        placeholder_data.update({
            "type": "dropdown",
            "default_index": default_index,
            "options": [{"display_name": key, "value": value} for key, value in placeholder.values.items()],
        })
    elif placeholder.input_type == InputType.Field:
        placeholder_data.update({
            "type": "textbox",
            "validators": [v.id for v in placeholder.validator_list],
        })

        if placeholder.default_function:
            placeholder_data["default_function"] = placeholder.default_function
        else:
            placeholder_data["default_value"] = placeholder.default_value

    else:
        raise Exception(f"Unexpected input type: {placeholder.input_type}")

    return placeholder_data


def validator_to_dict(v: Validator) -> dict:
    try:
        return {
            "id": v.id,
            "display_name": v.name,
            "rules": [validator_rule_to_dict(r) for r in v.rules],
        }
    except Exception as ex:
        raise PlaceholderConfigError(f"Error while converting validator '{v.name}' to dictionary: {ex}")

def validator_rule_to_dict(r: ValidatorRule) -> dict:
    data = {
        "severity": r.severity,
        "should_match": r.should_match,
        "error_message": r.error_message,
    }
    if r.match_function:
        if r.regex_string:
            raise PlaceholderConfigError(f"Error in rule: 'match_function' ({r.match_function}) and 'regex_string' ({r.regex_string}) are mutually exclusive, but both are defined")
        else:
            data["match_function"] = r.match_function
    else:
        if r.regex_string:
            data["regex"] = r.regex_string
        else:
            raise PlaceholderConfigError("Error in rule: You need to either specify 'match_function' or 'regex_string', but both are empty")

    return data

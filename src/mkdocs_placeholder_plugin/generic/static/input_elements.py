import html
# local files
from .. import warning
from ..config import Placeholder, InputType
from ..html_tag_parser import ParsedHtmlTag
from ..input_tag_handler import InputTagHandler


def create_static_input_field_replacer(placeholders: dict[str,Placeholder]) -> InputTagHandler:
    #@TODO: add this to normal page processing?
    def static_replacer_input_tag_modifier(handler, tag: str, parsed: ParsedHtmlTag) -> str:
        placeholder_name = parsed.attributes.get("data-input-for")
        if placeholder_name:
            if placeholder_name not in placeholders:
                # Print a warning if the placeholder does not exist
                warning(f"{handler.location} (static replacer) - Input element is linked to non-existent variable '{placeholder_name}'. Is this a typo or did you forget to set a default value for it?")
                return f'<input value="Undefined variable {html.escape(placeholder_name)}" disabled>'
            else:
                # Properly handle the different input element types
                return create_input_html_with_fallback(placeholders[placeholder_name])
        else:
            return tag

    return InputTagHandler(static_replacer_input_tag_modifier, False)

def create_input_html_with_fallback(placeholder: Placeholder) -> str:
    if placeholder.input_type == InputType.Checkbox:
        checked_by_default = placeholder.default_value == "checked"
        checked_attribute = " checked" if checked_by_default else ""
        return f'<input data-input-for="{placeholder.name}" type="checkbox" disabled{checked_attribute}>'
    elif placeholder.input_type == InputType.Dropdown:
        # We only show the name of the default option
        if placeholder.default_value:
            default_value = placeholder.default_value
        else:
            default_value = list(placeholder.values.keys())[0]
        return f'<select data-input-for="{placeholder.name}" disabled><option>{html.escape(default_value)}</option></select>'
    elif placeholder.input_type == InputType.Field:
        return f'<input data-input-for="{placeholder.name}" value="{html.escape(placeholder.default_value)}" disabled>'
    else:
        raise Exception(f"Unknown input type: {placeholder.input_type}")

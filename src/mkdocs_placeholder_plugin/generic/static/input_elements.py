import html
# local files
from .. import warning
from ..config.placeholder import Placeholder
from ..html_tag_parser import ParsedHtmlTag
from ..input_tag_handler import InputTagHandler
from .input_table import create_disabled_input_html


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
                return create_disabled_input_html(placeholders[placeholder_name])
        else:
            return tag

    return InputTagHandler(static_replacer_input_tag_modifier, False)


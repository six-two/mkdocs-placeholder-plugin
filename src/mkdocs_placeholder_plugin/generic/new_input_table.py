import html
# local
from .config import PlaceholderConfig, Placeholder, InputType

class TableGenerator:
    def __init__(self, config: PlaceholderConfig) -> None:
        self.config = config

    def generate_table_code(self, page_markdown: str, create_no_js_version: bool) -> str:
        # @TODO: read from config settings?
        column_list = ["description-or-name", "input"]

        no_js_table = ""
        if create_no_js_version:
            used_placeholders = self.get_placeholders_for_table(page_markdown)
            no_js_table = self.generate_table_html(used_placeholders, column_list)

        return f'<div class="auto-input-table" data-columns="{",".join(column_list)}">{no_js_table}</div>'


    def get_placeholders_for_table(self, page_markdown: str) -> list[Placeholder]:
        return [placeholder for placeholder in self.config.placeholders.values()
                if not placeholder.read_only and self.is_placeholder_on_page(placeholder, page_markdown)]

    def is_placeholder_on_page(self, placeholder: Placeholder, page_markdown: str) -> bool:
        if self.config.settings.dynamic_prefix + placeholder.name + self.config.settings.dynamic_suffix in page_markdown:
            return True
        elif self.config.settings.html_prefix + placeholder.name + self.config.settings.html_suffix in page_markdown:
            return True
        elif self.config.settings.normal_prefix + placeholder.name + self.config.settings.normal_suffix in page_markdown:
            return True
        elif self.config.settings.static_prefix + placeholder.name + self.config.settings.static_suffix in page_markdown:
            return True
        elif f'data-placeholder="{placeholder.name}"' in page_markdown:
            # Already preprocessed element that will use the placeholder via the dynamic replacement method
            # Looks like this: <span class="placeholder-value" data-placeholder="DEMO_FILENAME">file_to_transfer.txtp</span>
            return True
        else:
            return False

    def generate_table_html(self, placeholder_list: list[Placeholder], column_list: list[str]) -> str:
        #@TODO: actually handle the passed columns? Would be more complicated but also more consistent
        rows = []
        for placeholder in placeholder_list:
            description_or_name = placeholder.description if placeholder.description else placeholder.name
            input_element = create_disabled_input_html(placeholder)
            rows.append(f"<tr><td>{html.escape(description_or_name)}</td><td>{input_element}</td></tr>")

        table_header = "<thead><tr><th>Description / name</th><th>Input element</th></tr></thead>"
        table_body = f"<tbody>{''.join(rows)}</tbody>"
        return f"<table>{table_header}{table_body}</table>"


def create_disabled_input_html(placeholder: Placeholder) -> str:
    if placeholder.input_type == InputType.Checkbox:
        checked_by_default = placeholder.default_value == "checked"
        checked_attribute = " checked" if checked_by_default else ""
        return f'<input type="checkbox" disabled{checked_attribute}>'
    elif placeholder.input_type == InputType.Dropdown:
        # We only show the name of the default option
        if placeholder.default_value:
            default_value = placeholder.default_value
        else:
            default_value = list(placeholder.values.keys())[0]
        return f'<select disabled><option>{html.escape(default_value)}</option></select>'
    elif placeholder.input_type == InputType.Field:
        return f'<input value="{html.escape(placeholder.default_value)}" disabled>'
    else:
        raise Exception(f"Unknown input type: {placeholder.input_type}")

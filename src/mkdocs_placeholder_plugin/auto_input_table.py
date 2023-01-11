# local
from .plugin_config import PlaceholderPluginConfig
from .placeholder_data import Placeholder
from .input_table import PlaceholderTableSettings, InputTableGenerator


class AutoTableInserter:
    def __init__(self, placeholders: dict[str, Placeholder], plugin_config: PlaceholderPluginConfig) -> None:
        self.settings = PlaceholderTableSettings(
            table_type=plugin_config.table_default_type,
            entries=["auto"],
            show_readonly=False
        )
        self.input_table_generator = InputTableGenerator(placeholders, plugin_config.table_default_show_readonly,
                                        plugin_config.table_default_type, plugin_config.add_apply_table_column)
        if plugin_config.auto_placeholder_tables_javascript:
            # @TODO: read from plugin_config.table_default_type, once the column names are stable
            column_str = "description-or-name,input"
            self.input_table_string = f'<div class="auto-input-table" data-columns="{column_str}"></div>'
        else:
            self.input_table_string = ""

        self.admonitions = plugin_config.auto_placeholder_tables_collapsible

    def add_to_page(self, markdown: str) -> str:
        if self.input_table_generator:
            table_markdown = self.input_table_generator.create_placeholder_input_table(self.settings, markdown)
        else:
            page_has_placeholders = self.input_table_generator.auto_detect_placeholders_used_in_page(markdown)
            table_markdown = self.input_table_string if page_has_placeholders else ""

        if table_markdown:
            if self.admonitions:
                # "???+": Needs to be expanded by default, since otherwise it will be collapsed on every reload (which may be whenever a value is changed)
                table_markdown = ('???+ note "Change placeholder values"\n' + table_markdown).replace("\n", "\n    ")

            return table_markdown + "\n" + markdown
        else:
            # No entries in table -> no placeholders on page -> we do not need to modify it
            return markdown

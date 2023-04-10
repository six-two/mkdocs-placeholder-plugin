# local
from ..mkdocs.plugin_config import PlaceholderPluginConfig
from .config.placeholder import Placeholder
from .input_table import PlaceholderTableSettings, InputTableGenerator


class AutoTableInserter:
    def __init__(self, placeholders: dict[str, Placeholder], plugin_config: PlaceholderPluginConfig) -> None:
        self.settings = PlaceholderTableSettings(
            table_type=plugin_config.table_default_type,
            entries=["auto"],
            show_readonly=False
        )
        self.hide_read_only = True
        self.read_only_placeholder_names = set([x.name for x in placeholders.values() if x.read_only])
        self.input_table_generator = InputTableGenerator(placeholders, False,
                                        plugin_config.table_default_type, False)

        # @TODO: read from plugin_config.table_default_type, once the column names are stable
        column_str = "description-or-name,input"
        self.input_table_string = f'<div class="auto-input-table" data-columns="{column_str}"></div>'

        self.admonitions = plugin_config.auto_placeholder_tables_collapsible

    def add_to_page(self, markdown: str) -> str:
        if self.input_table_string:
            table_markdown = self.get_javascript_table_for_page(markdown)
        else:
            # Generate a custom placeholder input table for this page
            # @TODO: remove?
            table_markdown = self.input_table_generator.create_placeholder_input_table(self.settings, markdown)

        if table_markdown:
            if self.admonitions:
                # "???+": Needs to be expanded by default, since otherwise it will be collapsed on every reload (which may be whenever a value is changed)
                table_markdown = ('???+ note "Change placeholder values"\n' + table_markdown).replace("\n", "\n    ")

            return table_markdown + "\n" + markdown
        else:
            # No entries in table -> no placeholders on page -> we do not need to modify it
            return markdown

    def get_javascript_table_for_page(self, markdown: str) -> str:
        # @TODO generate static content if wanted
        # @TODO: check for recursive 

        # We use the javascript version, so we just need to add the same string for each page.
        # But we check if the page contains any placeholders that should be shown, so that we can skip pages we do not need to modify
        used_placeholders = self.input_table_generator.auto_detect_placeholders_used_in_page(markdown)
        if used_placeholders and self.hide_read_only:
            # This checks whether all placeholders are readonly
            for placeholder in used_placeholders:
                if placeholder not in self.read_only_placeholder_names:
                    # At least one non-read-only placeholder exists -> show the table
                    return self.input_table_string
            # All placeholders are read only and should not be shown -> do not show the table
            return ""
        else:
            # Nothing needs to be hidden, so the check is straight forward
            return self.input_table_string if used_placeholders else ""

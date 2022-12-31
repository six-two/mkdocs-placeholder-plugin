import html
import re
from typing import NamedTuple
# pip dependencies
import mkdocs
# local files
from .placeholder_data import Placeholder
from .html_tag_parser import parse_html_tag

def reload_on_click(text: str) -> str:
    return f'<span class="button-reload" style="cursor: pointer" onclick="window.location.reload()">{text}</span>'

INPUT_TABLE_PLACEHOLDER = re.compile("<placeholdertable[^>]*>")
RELOAD_ROW = reload_on_click("Apply the new values") + " | " + reload_on_click("by clicking on this text") + "\n"


class PlaceholderTableSettings(NamedTuple):
    table_type: str
    # ["auto"], ["all"], or a list of explicit placeholder names
    entries: list[str]
    show_readonly: bool



class InputTableGenerator:
    def __init__(self, placeholders: dict[str,Placeholder], default_show_readonly: bool, default_table_type: str, add_apply_table_column: bool) -> None:
        self.placeholders = placeholders
        self.default_table_type = default_table_type
        self.default_show_readonly = default_show_readonly
        self.add_apply_table_column = add_apply_table_column

    def handle_markdown(self, page_markdown: str) -> str:
        matches = list(INPUT_TABLE_PLACEHOLDER.finditer(page_markdown))
        # Iterate in reverse order to not screw up the indices used when replacing text
        for match in reversed(matches):
            tag_html = match.group(0)
            settings = self.parse_placeholder_table_tag(tag_html)
            markdown_table = self.create_placeholder_input_table(settings, page_markdown)

            start, end = match.span()
            page_markdown = page_markdown[:start] + markdown_table + page_markdown[end:]
        return page_markdown


    def parse_placeholder_table_tag(self, full_tag_html: str) -> PlaceholderTableSettings:
        parsed = parse_html_tag(full_tag_html)
        
        if parsed.tag != "placeholdertable":
            raise Exception(f"Expected placeholdertable tag, but got '{parsed.tag}'")


        table_type = parsed.attributes.get("type", self.default_table_type)

        entries_string = parsed.attributes.get("entries", "auto")
        # parse entries as a comma separated list with optional whitespace
        entries = [x.strip() for x in entries_string.split(",") if x.strip()]

        try:
            show_readonly_string = parsed.attributes["show-readonly"].lower()
            if show_readonly_string in ["0", "off", "disabled", "false"]:
                show_readonly = False
            elif show_readonly_string in ["1", "on", "enabled", "true"]:
                show_readonly = True
            else:
                raise mkdocs.exceptions.PluginError(f"[placeholder] Expected boolean value ('true' or 'false') for 'show-readonly', but got '{show_readonly_string}'")
        except KeyError:
            show_readonly = self.default_show_readonly

        return PlaceholderTableSettings(
            table_type=table_type,
            entries=entries,
            show_readonly=show_readonly,
        )

    def auto_detect_placeholders_used_in_page(self, page: str) -> list[str]:
        """
        This tries to be a "smart" implementation. As such it actually performs replacements,
        since they may (by default) introduce new placeholders.
        Basically it performs all replacements as they normally would be done and checks for each placeholder, 
        if the text was changed afterwards.
        """
        used_placeholders: list[str] = []
        for placeholder in self.placeholders.values():
            after_replacement = page.replace(f"x{placeholder.name}x", placeholder.default_value)
            if page != after_replacement:
                # The page was changed -> the placeholder must exist in the page
                page = after_replacement
                used_placeholders.append(placeholder.name)

        return used_placeholders


    def create_placeholder_input_table(self, settings: PlaceholderTableSettings, page_markdown: str) -> str:
        placeholder_names = settings.entries
        if placeholder_names == ["all"]:
            # use all placeholders
            placeholder_entries = list(self.placeholders.values())
        else:
            if placeholder_names == ["auto"]:
                # auto detect placeholders
                placeholder_names = self.auto_detect_placeholders_used_in_page(page_markdown)
            
            # resolve given names to placeholders
            try:
                placeholder_entries = [self.placeholders[name] for name in placeholder_names]
            except KeyError as e:
                raise mkdocs.exceptions.PluginError(f"[placeholder] Unknown placeholder: '{e}'")

        if not settings.show_readonly:
            # remove all placeholders that are marked as readonly
            placeholder_entries = [entry for entry in placeholder_entries if not entry.read_only]

        if not placeholder_entries:
            # No table entries -> hide the whole table
            return ""

        if settings.table_type == "simple":
            return self.create_simple_placeholder_table(placeholder_entries)
        elif settings.table_type == "description":
            return self.create_description_placeholder_table(placeholder_entries)
        else:
            raise mkdocs.exceptions.PluginError(f"[placeholder] Unknown table type: '{settings.table_type}'")


    def create_simple_placeholder_table(self, placeholder_entries: list[Placeholder]) -> str:
        markdown_table = "Variable | Value\n---|---\n"
        for placeholder in placeholder_entries:
            name = html.escape(placeholder.name)
            markdown_table += f'{name} | <input data-input-for="{name}">\n'

        if self.add_apply_table_column:
            markdown_table += RELOAD_ROW
        return markdown_table + "\n"

    def create_description_placeholder_table(self, placeholder_entries: list[Placeholder]) -> str:
        markdown_table = "Variable | Value | Description\n---|---|---\n"
        for placeholder in placeholder_entries:
            # HTML escape contents for security
            name = html.escape(placeholder.name)
            # Also escape/replace characters that may break my table
            description = html.escape(placeholder.description).replace("|", "&#124;").replace("\r", " ").replace("\n", " ")
            markdown_table += f'{name} | <input data-input-for="{name}"> | {description}\n'
        
        if self.add_apply_table_column:
            markdown_table += RELOAD_ROW
        return markdown_table + "\n"


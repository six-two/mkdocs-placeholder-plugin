
# local
from .config import PlaceholderConfig
from .static.placeholder_replacer import DynamicPlaceholderPreprocessor
from .static.input_table import TableGenerator
from .static.input_elements import create_static_input_field_replacer
from .input_tag_handler import create_normal_input_class_handler

class PageProcessor:
    def __init__(self, config: PlaceholderConfig) -> None:
        self.config = config
        self.dynamic_placeholder_preprocessor = DynamicPlaceholderPreprocessor(config)
        self.table_generator = TableGenerator(config)

        # Set the value for inputs to inform the user to enable JavaScript
        # Line numbers in output are disabled, since we need to call this after the markdown was parsed.
        # Otherwise stuff in listings and co may be unintentianally modified/checked
        self.input_tag_modifier = create_normal_input_class_handler(config.placeholders, add_line_in_warning=False)



    def process_page_markdown(self, markdown: str) -> str:
        if True: #@TODO
            markdown = self.dynamic_placeholder_preprocessor.handle_markdown_page(markdown)
        if self.config.settings.auto_placeholder_tables:
            markdown = "<PLACEHOLDER_PLUGIN_AUTO_TABLE_HERE>\n\n" + markdown
        return markdown


    def process_page_html(self, file_path: str, html: str) -> str:
        if True: #@TODO
            html = self.dynamic_placeholder_preprocessor.handle_html_page(html)

            dynamic_table_with_fallback = self.table_generator.generate_table_code(html, True)
            html = html.replace("<PLACEHOLDER_PLUGIN_AUTO_TABLE_HERE>", dynamic_table_with_fallback) #@TODO: search for all auto tables

        # file_path = page.file.src_path
        return self.input_tag_modifier.process_string(file_path, html)

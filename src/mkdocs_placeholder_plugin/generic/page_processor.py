
# local
from .config import PlaceholderConfig
from .static.placeholder_replacer import DynamicPlaceholderPreprocessor
from .static.table_replacer import StaticHtmlElementTableFallbackReplacer
from .static.table_generator import TableGenerator
from .static.input_elements import StaticInputElementReplacer
from .html_tag_handler import NormalHtmlInputElementHandler

class PageProcessor:
    def __init__(self, config: PlaceholderConfig) -> None:
        self.config = config
        self.dynamic_placeholder_preprocessor = DynamicPlaceholderPreprocessor(config)
        self.table_generator = TableGenerator(config)

        # Set the value for inputs to inform the user to enable JavaScript
        # Line numbers in output are disabled, since we need to call this after the markdown was parsed.
        # Otherwise stuff in listings and co may be unintentianally modified/checked
        self.input_tag_modifier = NormalHtmlInputElementHandler(config.placeholders, add_line_in_warning=False)

        self.static_input_tag_modifer = StaticInputElementReplacer(config.placeholders, add_line_in_warning=False)

        if self.config.settings.create_no_js_fallback:
            self.html_table_replacer = StaticHtmlElementTableFallbackReplacer(config, add_line_in_warning=False)


    def process_page_markdown(self, markdown: str) -> str:
        if self.config.settings.create_no_js_fallback:
            markdown = self.dynamic_placeholder_preprocessor.handle_markdown_page(markdown)
        
        if self.config.settings.auto_placeholder_tables:
            # markdown = "<PLACEHOLDER_PLUGIN_AUTO_TABLE_HERE>\n\n" + markdown
            markdown = '<div class="auto-input-table" data-columns="name,description,input"></div>\n\n' + markdown
        
        return markdown


    def process_page_html(self, file_path: str, html: str) -> str:
        if self.config.settings.create_no_js_fallback:
            html = self.dynamic_placeholder_preprocessor.handle_html_page(html)

            html = self.html_table_replacer.process_string(file_path, html)

        # dynamic_table_with_fallback = self.table_generator.generate_table_code(html, self.config.settings.create_no_js_fallback)
        # html = html.replace("<PLACEHOLDER_PLUGIN_AUTO_TABLE_HERE>", dynamic_table_with_fallback) #@TODO: search for all auto tables, only do it if self.config.settings.create_no_js_fallback is true


        if self.config.settings.create_no_js_fallback:
            html = self.static_input_tag_modifer.process_string(file_path, html)
        else:
            html = self.input_tag_modifier.process_string(file_path, html)

        return html

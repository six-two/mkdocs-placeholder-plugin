
# local
from .config import PlaceholderConfig
from .static.placeholder_replacer import DynamicPlaceholderPreprocessor
from .static.table_replacer import StaticHtmlElementTableFallbackReplacer
from .static.table_generator import TableGenerator
from .static.input_elements import StaticInputElementReplacer
from .html_tag_handler import NormalHtmlInputElementHandler, HtmlTagHandler

END_OF_TITLE = "</h1>"

class PageProcessor:
    def __init__(self, config: PlaceholderConfig) -> None:
        self.config = config
        self.dynamic_placeholder_preprocessor = DynamicPlaceholderPreprocessor(config)
        self.table_generator = TableGenerator(config)
        self.generate_fallback = self.config.settings.create_no_js_fallback

        # Set the value for inputs to inform the user to enable JavaScript
        # Line numbers in output are disabled, since we need to call this after the markdown was parsed.
        # Otherwise stuff in listings and co may be unintentianally modified/checked
        add_line_in_warning = False
        if self.generate_fallback:
            self.html_table_replacer = StaticHtmlElementTableFallbackReplacer(config, add_line_in_warning)
        
        self.input_tag_modifier: HtmlTagHandler = StaticInputElementReplacer(config.placeholders, add_line_in_warning) \
            if self.generate_fallback else NormalHtmlInputElementHandler(config.placeholders, add_line_in_warning)

    def process_page_markdown(self, markdown: str) -> str:
        if self.config.settings.create_no_js_fallback:
            markdown = self.dynamic_placeholder_preprocessor.handle_markdown_page(markdown)
                
        return markdown

    def process_page_html(self, file_path: str, html: str) -> str:
        if self.config.settings.auto_placeholder_tables:
            # Add directly behind the title. Looks better than simply appending before everything else
            html = html.replace(END_OF_TITLE, f'{END_OF_TITLE}<div class="auto-input-table" data-hide-empty data-columns="description-or-name,input"></div>', 1) 

        if self.config.settings.create_no_js_fallback:
            html = self.dynamic_placeholder_preprocessor.handle_html_page(html)
            html = self.html_table_replacer.process_string(file_path, html)

        html = self.input_tag_modifier.process_string(file_path, html)
        return html

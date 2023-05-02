
# local
from .config import PlaceholderConfig
from ..generic.auto_input_table import AutoTableInserter

class PageProcessor:
    def __init__(self, config: PlaceholderConfig) -> None:
        self.config = config
        self.auto_table_inserter = AutoTableInserter(self.placeholders, self.config)

    def process_page_markdown(self, page_name, page_markdown) -> str:
        if self.config.settings.auto_placeholder_tables:
            markdown = self.auto_table_inserter.add_to_page(markdown)
        return self.table_generator.handle_markdown(markdown)

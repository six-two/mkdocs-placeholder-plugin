
# local
from .config import PlaceholderConfig

class PageProcessor:
    def __init__(self, config: PlaceholderConfig) -> None:
        self.config = config

    def process_page_markdown(self, page_name, page_markdown) -> str:
        #@TODO
        return page_markdown

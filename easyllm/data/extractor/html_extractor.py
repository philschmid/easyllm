from pydantic import BaseModel

#
from inscriptis import get_text
from inscriptis.css_profiles import CSS_PROFILES
from inscriptis.model.config import ParserConfig
from readability import Document

INSCRIPTIS_CONFIG = ParserConfig(css=CSS_PROFILES["strict"])


class HtmlExtractor(BaseModel):
    """
    Desc: Extracts text from the HTML document using mozzilas readability and inscriptis.
    """

    name: str = "html_extractor"
    min_doc_length: int = 25

    def __call__(self, document: str) -> str:
        parsed_doc = Document(document, min_text_length=self.min_doc_length)
        clean_html = parsed_doc.summary(html_partial=True)
        content = get_text(clean_html, INSCRIPTIS_CONFIG).strip()
        return content

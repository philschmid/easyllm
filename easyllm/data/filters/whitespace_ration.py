import re

from pydantic import BaseModel


class WhitespaceRatioFilter(BaseModel):
    """
    Desc: If more than 25% of the document are bulletpoints then remove
    """

    name: str = "whitespace_ratio"
    regex: re.Pattern = re.compile(r"\s")
    remove_percentage: float = 0.25

    def __call__(self, text):
        # whitespace characters
        whitespace_count = len(self.regex.findall(text))
        text_length = len(text)
        # check if the ratio of whitespace to text is greater than the remove percentage
        if whitespace_count / text_length > self.remove_percentage:
            return True
        # otherwise keep
        return False

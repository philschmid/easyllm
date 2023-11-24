import re

from pydantic import BaseModel


class ParenthesesRationFilter(BaseModel):
    """
    Desc: If more than 10% of the document are Parentheses then remove
    """

    name: str = "parentheses_ratio"
    regex: re.Pattern = re.compile(r"\[|\]|\(|\)|{|}|⟨|⟩")
    remove_percentage: float = 0.1

    def __call__(self, text):
        # parentheses characters
        parentheses_count = len(self.regex.findall(text))
        sentence_length = len(text)
        # check if the ratio of parentheses to text is greater than the remove percentage
        if parentheses_count / sentence_length > self.remove_percentage:
            return True
        # otherwise keep
        return False

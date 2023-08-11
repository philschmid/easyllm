import re

from pydantic import BaseModel


class LengthFilter(BaseModel):
    """
    Desc: Removes documents below or above a certain length of words
    """

    name: str = "length"
    min_length: int = 10
    max_length: int = 1_000_000

    def __call__(self, text):
        num_words = len(text.split())

        if num_words < self.min_length or num_words > self.max_length:
            return True
        # otherwise keep
        return False

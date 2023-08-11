import re

from pydantic import BaseModel


class LongWordFilter(BaseModel):
    """
    Ref: C4 Raffel et al.
    Desc: If document includes words with > 1000 character are removed, e.g. js or minified files.
    """

    name: str = "long_word"
    max_length: int = 1000

    def __call__(self, text):
        words = text.split()
        max_len = max(len(word) for word in words)
        if max_len > self.max_length:
            return True
        # otherwise keep
        return False

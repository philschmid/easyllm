import re

from pydantic import BaseModel


class SymbolToWordFilter(BaseModel):
    """
    Ref: Gopher (Rae et al., 2021)
    Desc: If more than 10% of the document are symbols (hashes [#] or ellipsis (...)) then remove
    """

    name: str = "symbol_to_word"
    regex: re.Pattern = r"(\#+|(\.{3,}))(?!\w)"
    remove_percentage: float = 0.1

    def __call__(self, text: str):
        num_hashes = len(re.findall(r"\#+", text))
        num_ellipses = len(re.findall(r"\.{3,}", text))
        num_words = len(re.findall(r"\w+", text))

        # check if there are any words in the text
        if num_words == 0:
            return True

        hash_ratio = num_hashes / num_words
        ellipses_ratio = num_ellipses / num_words

        # if the percentage is greater than the remove_percentage then remove
        if hash_ratio > self.remove_percentage or ellipses_ratio > self.remove_percentage:
            return True

        # otherwise keep
        return False

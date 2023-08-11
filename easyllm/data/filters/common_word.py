from typing import List

from pydantic import BaseModel

COMMON_WORDS_EN = ["the", "be", "to", "of", "and", "that", "have", "with", "this"]
COMMON_WORDS_DE = ["der", "die", "das", "er" "sein", "zu", "ist", "war", "von", "und", "haben", "mit"]


class CommonWordFilter(BaseModel):
    """
    Ref: Gopher (Rae et al., 2021)
    Desc: Makes sure that the document contains at least 2 common words if not remove
    """

    name: str = "common_word"
    common_words: List[str] = COMMON_WORDS_EN
    n: int = 2

    def __call__(self, text):
        words = text.split()
        common_word_counter = 0
        # count the number of common words
        for word in words:
            if word.lower() in self.common_words:
                common_word_counter += 1
            if common_word_counter >= self.n:
                return False
        # otherwise remove
        return True

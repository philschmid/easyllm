import re
from typing import List

from pydantic import BaseModel


class PunctuationFilter(BaseModel):
    """
    Ref: C4 Raffel et al.
    Desc: If less than 15% of the sentences end with a punctuation mark then remove
    """

    name: str = "punctuation"
    punctuations: List[str] = [".", "!", "?"]
    remove_percentage: float = 0.15

    def __call__(self, text):
        sentences = text.split("\n")
        # count the number of sentences not ending with a punctuation mark
        num_sentences_wo_p = sum(
            1 for sentence in sentences if sentence[-1] not in self.punctuations
        )
        # check if the ratio of sentences not ending with a punctuation mark is greater than the remove percentage
        if num_sentences_wo_p / len(sentences) > self.remove_percentage:
            return True
        # otherwise keep
        return False
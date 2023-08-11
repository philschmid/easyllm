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
        # count the number of sentences ending with a punctuation mark
        punc_counter = 0
        for sentence in sentences:
            for punc in self.punctuations:
                if sentence.endswith(punc):
                    punc_counter += 1
                    break
        # check if the ratio of sentences not ending with a punctuation mark is greater than the remove percentage
        if 1 - (punc_counter / len(sentences)) > self.remove_percentage:
            return True
        # otherwise keep
        return False


class EllipsisFilter(BaseModel):
    """
    Ref: C4 Raffel et al.
    Desc: If more than 30% of the sentences endwith an elipsis then remove
    """

    name: str = "ellipsis"
    ellipsis: List[str] = ["...", "[...]", "…", "(...)", "[…]", "-»", "read more..", "read more"]
    remove_percentage: float = 0.3

    def __call__(self, text):
        sentences = text.split("\n")
        # count the number of sentences ending with an ellipsis
        ellipsis_counter = 0
        for sentence in sentences:
            for ellipsis in self.ellipsis:
                if sentence.endswith(ellipsis):
                    ellipsis_counter += 1
                    break
        # check if the ratio of sentences ending with an ellipsis is greater than the remove percentage
        if ellipsis_counter / len(sentences) > self.remove_percentage:
            return True
        # otherwise keep
        return False

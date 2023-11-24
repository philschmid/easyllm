from collections import Counter
from itertools import chain

from pydantic import BaseModel


def get_ngrams(input_list, n):
    return list(zip(*[input_list[i:] for i in range(n)]))


class TopNGramsFilter(BaseModel):
    """
    Ref: Gopher (Rae et al., 2021)
    Desc: If the document shrinks by > 20% after removing top n-grams then remove
    """

    name: str = "top_n_grams"
    remove_percentage: float = 0.2
    n: int = 2

    def __call__(self, text):
        words = text.split()
        if len(words) <= self.n:
            return True
        ngrams = get_ngrams(words, self.n)
        n_grams = Counter(chain(ngrams))
        most_common = n_grams.most_common(1)[0][0]

        if n_grams[most_common] / len(n_grams) > self.remove_percentage:
            return True
        # otherwise keep
        return False

import re

from pydantic import BaseModel


class NonAlphaNumericFilter(BaseModel):
    """
    Ref: Gopher (Rae et al., 2021)
    Desc: If more than 20% of the document is non-alphanumeric then remove
    """

    name: str = "non_alpha_numeric"
    regex: re.Pattern = re.compile("[^a-zA-Z0-9\s]")
    cutoff_percentage: float = 0.2

    def __call__(self, text):
        num_characters = len(text)
        # check if there are any characters in the text
        if num_characters == 0:
            return True
        # calculate the percentage of non-alphanumeric characters
        percentage = 1 - ((num_characters - len(self.regex.findall(text))) / num_characters)
        # if the percentage is greater than the cutoff_percentage then remove
        if percentage > self.cutoff_percentage:
            return True
        # otherwise keep
        return False

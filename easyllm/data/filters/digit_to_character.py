import re

from pydantic import BaseModel


class DigitToCharacter(BaseModel):
    """
    Desc: If more than 20% of the document are digits then remove
    """

    name: str = "digit_to_character"
    remove_percentage: float = 0.2

    def __call__(self, text):
        digits = re.findall(r"\d", text)
        num_digits = len(digits)
        total_chars = len(text)
        # check if there are any characters in the text
        if num_digits / total_chars > self.remove_percentage:
            return True
        # otherwise keep
        return False

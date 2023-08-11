from pydantic import BaseModel


class RepeatedLinesFilter(BaseModel):
    """
    Ref: Gopher (Rae et al., 2021)
    Desc: If the document shrinks by > 30% after removing repeated lines then remove
    """

    name: str = "repeated_lines"
    remove_percentage: float = 0.3

    def __call__(self, text):
        # split the text into lines
        lines = text.split("\n")
        # remove empty lines
        lines = [line for line in lines if line.strip()]
        if len(lines) == 0:
            return True
        # remove repeated lines
        unique_lines = list(set(lines))
        # calculate the percentage of lines removed
        if len(unique_lines) / len(lines) < self.remove_percentage:
            return True
        # otherwise keep
        return False


class RepeatedParagraphFilter(BaseModel):
    """
    Ref: Gopher (Rae et al., 2021)
    Desc: If the document shrinks by > 30% after removing repeated paragraphs then remove
    """

    name: str = "repeated_paragraph"
    remove_percentage: float = 0.3

    def __call__(self, text):
        # split the text into lines
        paragraphes = text.split("\n\n")
        # remove empty paragraph
        paragraphes = [p for p in paragraphes if p.strip()]
        if len(paragraphes) == 0:
            return True
        # remove repeated paragraphes
        unique_paragraphes = list(set(paragraphes))
        # calculate the percentage of lines removed
        if len(unique_paragraphes) / len(paragraphes) < self.remove_percentage:
            return True
        # otherwise keep
        return False

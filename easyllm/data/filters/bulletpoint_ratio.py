from typing import List

from pydantic import BaseModel


class BulletpointRatioFilter(BaseModel):
    """
    Ref: Gopher (Rae et al., 2021)
    Desc: If more than 90% of the document are bulletpoints then remove
    """

    name: str = "bulletpoint_ratio"
    potential_bullet_points: List[str] = [
        "•",
        "‣",
        "⁃",
        "⁌",
        "⁍",
        "∙",
        "○",
        "●",
        "◘",
        "◦",
        "⦾",
        "⦿",
        "-",
    ]
    remove_percentage: float = 0.9

    def __call__(self, text):
        # split text into lines
        lines = text.split("\n")
        num_bullet_points = 0
        for line in lines:
            # check if the line is a bullet point
            if line.startswith(tuple(self.potential_bullet_points)):
                num_bullet_points += 1
        # check if the ratio of bullet points to lines is greater than the remove percentage
        if num_bullet_points / len(lines) > self.remove_percentage:
            return True
        # otherwise keep
        return False

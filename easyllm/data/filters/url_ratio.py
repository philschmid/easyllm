import re

from pydantic import BaseModel


class UrlRatioFilter(BaseModel):
    """
    Desc: If more than 20% of the document are urls then remove
    """

    name: str = "url_ratio"
    regex: re.Pattern[
        str
    ] = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    remove_percentage: float = 0.2

    def __call__(self, text):
        # find all urls
        urls = re.findall(self.regex, text)
        # check if the ratio of urls to words is greater than the remove percentage
        if len(urls) / len(text.split()) > self.remove_percentage:
            return True
        # otherwise keep
        return False

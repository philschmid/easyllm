import re

from pydantic import BaseModel


class CookieBannerFilter(BaseModel):
    """
    Ref: C4 Raffel et al.
    Desc: Removes documents if more than 40% of the documents include terms for cookies, tos, privacy policy, etc. Requires external list.
    """

    name: str = "cookie_banner"
    regex: re.Pattern = re.compile(r"(terms of use|privacy policy|copyright|all rights reserved)", re.IGNORECASE)
    remove_percentage: float = 0.4

    def __call__(self, text):
        # check if the regex matches
        raise NotImplementedError("CookieBannerFilter not implemented yet")

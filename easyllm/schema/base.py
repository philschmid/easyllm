from typing import Literal, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "function", "system"]
    content: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: Optional[int] = None
    total_tokens: int

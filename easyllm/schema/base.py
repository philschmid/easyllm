from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "function", "system"]
    content: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

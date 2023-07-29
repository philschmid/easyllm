import time
from typing import Dict, List, Literal, Optional, Union

from nanoid import generate
from pydantic import BaseModel, Field

from easyllm.schema.base import ChatMessage, Usage


# More documentation https://platform.openai.com/docs/api-reference/chat/create
# adapted from https://github.com/lm-sys/FastChat/blob/main/fastchat/protocol/openai_api_protocol.py
class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = 0.9
    top_p: Optional[float] = 0.6
    top_k: Optional[int] = 10
    n: Optional[int] = 1
    max_tokens: Optional[int] = 1024
    stop: Optional[List[str]] = None
    stream: Optional[bool] = False
    frequency_penalty: Optional[float] = 1.0
    user: Optional[str] = None


# adapted from https://github.com/lm-sys/FastChat/blob/main/fastchat/protocol/openai_api_protocol.py
class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[Literal["stop", "length"]] = None


# adapted from https://github.com/lm-sys/FastChat/blob/main/fastchat/protocol/openai_api_protocol.py
class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"hf-{generate(size=10)}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: Usage


# adapted from https://github.com/lm-sys/FastChat/blob/main/fastchat/protocol/openai_api_protocol.py
class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


# adapted from https://github.com/lm-sys/FastChat/blob/main/fastchat/protocol/openai_api_protocol.py
class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: Union[DeltaMessage, Dict[str, str]]
    finish_reason: Optional[Literal["stop", "length"]] = None


# adapted from https://github.com/lm-sys/FastChat/blob/main/fastchat/protocol/openai_api_protocol.py
class ChatCompletionStreamResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"hf-{generate(size=10)}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionResponseStreamChoice]

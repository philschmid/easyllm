import time
from typing import Any, Dict, List, Literal, Optional, Union

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


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[Literal["stop_sequence", "length", "eos_token"]] = None


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"hf-{generate(size=10)}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: Optional[str] = "custom"
    choices: List[ChatCompletionResponseChoice]
    usage: Usage


class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: Union[DeltaMessage, Dict[str, str]]
    finish_reason: Optional[Literal["stop", "length"]] = None


class ChatCompletionStreamResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"hf-{generate(size=10)}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: Optional[str] = None
    choices: List[ChatCompletionResponseStreamChoice]


class CompletionRequest(BaseModel):
    model: Optional[str] = None
    prompt: Union[str, List[Any]]
    suffix: Optional[str] = None
    temperature: Optional[float] = 0.9
    top_p: Optional[float] = 0.6
    top_k: Optional[int] = 10
    n: Optional[int] = 1
    max_tokens: Optional[int] = 1024
    stop: Optional[List[str]] = None
    stream: Optional[bool] = False
    frequency_penalty: Optional[float] = 1.0
    user: Optional[str] = None
    logprobs: Optional[bool] = None
    echo: Optional[bool] = False
    user: Optional[str] = None


class CompletionResponseChoice(BaseModel):
    index: int
    text: str
    logprobs: Union[Optional[List[Dict[str, Any]]], float] = None
    finish_reason: Optional[Literal["stop_sequence", "length", "eos_token"]] = None


class CompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"hf-{generate(size=10)}")
    object: str = "text.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: Optional[str] = "custom"
    choices: List[CompletionResponseChoice]
    usage: Usage


class CompletionResponseStreamChoice(BaseModel):
    index: int
    text: str
    logprobs: Optional[float] = None
    finish_reason: Optional[Literal["stop_sequence", "length", "eos_token"]] = None


class CompletionStreamResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"hf-{generate(size=10)}")
    object: str = "text.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: Optional[str] = "custom"
    choices: List[CompletionResponseStreamChoice]


class EmbeddingsRequest(BaseModel):
    model: Optional[str] = None
    input: Union[str, List[Any]]
    user: Optional[str] = None


class EmbeddingsObjectResponse(BaseModel):
    index: int
    object: str = "embedding"
    embedding: List[float]


class EmbeddingsResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingsObjectResponse]
    model: Optional[str] = "custom"
    usage: Usage

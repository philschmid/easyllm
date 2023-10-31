import json
import logging
import os
from typing import Any, Dict, List, Optional

from nanoid import generate

from easyllm.prompt_utils.base import build_prompt, buildBasePrompt
from easyllm.schema.base import ChatMessage, Usage, dump_object
from easyllm.schema.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    DeltaMessage,
)
from easyllm.utils import setup_logger
from easyllm.utils.aws import get_bedrock_client

logger = setup_logger()

# default parameters
api_type = "bedrock"
api_aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID", None)
api_aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
api_aws_session_token = os.environ.get("AWS_SESSION_TOKEN", None)

client = get_bedrock_client(
    aws_access_key_id=api_aws_access_key,
    aws_secret_access_key=api_aws_secret_key,
    aws_session_token=api_aws_session_token,
)


SUPPORTED_MODELS = [
    "anthropic.claude-v2",
]
model_version_mapping = {"anthropic.claude-v2": "bedrock-2023-05-31"}

api_version = os.environ.get("BEDROCK_API_VERSION", None) or "bedrock-2023-05-31"
prompt_builder = os.environ.get("BEDROCK_PROMPT", None)
stop_sequences = []


def stream_chat_request(client, body, model):
    """Utility function for streaming chat requests."""
    id = f"hf-{generate(size=10)}"
    response = client.invoke_model_with_response_stream(
        body=json.dumps(body), modelId=model, accept="application/json", contentType="application/json"
    )
    stream = response.get("body")

    yield dump_object(
        ChatCompletionStreamResponse(
            id=id,
            model=model,
            choices=[ChatCompletionResponseStreamChoice(index=0, delta=DeltaMessage(role="assistant"))],
        )
    )
    # yield each generated token
    reason = None
    for _idx, event in enumerate(stream):
        chunk = event.get("chunk")
        if chunk:
            chunk_obj = json.loads(chunk.get("bytes").decode())
            text = chunk_obj["completion"]
            yield dump_object(
                ChatCompletionStreamResponse(
                    id=id,
                    model=model,
                    choices=[ChatCompletionResponseStreamChoice(index=0, delta=DeltaMessage(content=text))],
                )
            )
    yield dump_object(
        ChatCompletionStreamResponse(
            id=id,
            model=model,
            choices=[ChatCompletionResponseStreamChoice(index=0, finish_reason=reason, delta={})],
        )
    )


class ChatCompletion:
    @staticmethod
    def create(
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.9,
        top_p: float = 0.6,
        top_k: Optional[int] = 10,
        n: int = 1,
        max_tokens: int = 1024,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        frequency_penalty: Optional[float] = 1.0,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Creates a new chat completion for the provided messages and parameters.

        Args:
            messages (`List[ChatMessage]`): to use for the completion.
            model (`str`, *optional*, defaults to None): The model to use for the completion. If not provided,
                defaults to the base url.
            temperature (`float`, defaults to 0.9): The temperature to use for the completion.
            top_p (`float`, defaults to 0.6): The top_p to use for the completion.
            top_k (`int`, *optional*, defaults to 10): The top_k to use for the completion.
            n (`int`, defaults to 1): The number of completions to generate.
            max_tokens (`int`, defaults to 1024): The maximum number of tokens to generate.
            stop (`List[str]`, *optional*, defaults to None): The stop sequence(s) to use for the completion.
            stream (`bool`, defaults to False): Whether to stream the completion.
            frequency_penalty (`float`, *optional*, defaults to 1.0): The frequency penalty to use for the completion.
            debug (`bool`, defaults to False): Whether to enable debug logging.

        Tip: Prompt builder
            Make sure to always use a prompt builder for your model.
        """
        if debug:
            logger.setLevel(logging.DEBUG)

        # validate it model is in model_mapping
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"Model {model} is not supported. Supported models are: {SUPPORTED_MODELS}")

        request = ChatCompletionRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            n=n,
            max_tokens=max_tokens,
            stop=stop,
            stream=stream,
            frequency_penalty=frequency_penalty,
        )

        if prompt_builder is None:
            logger.warn(
                f"""huggingface.prompt_builder is not set.
Using default prompt builder for. Prompt sent to model will be:
----------------------------------------
{buildBasePrompt(request.messages)}.
----------------------------------------
If you want to use a custom prompt builder, set bedrock.prompt_builder to a function that takes a list of messages and returns a string.
You can also use existing prompt builders by importing them from easyllm.prompt_utils"""
            )
            prompt = buildBasePrompt(request.messages)
        else:
            prompt = build_prompt(request.messages, prompt_builder)

        # create stop sequences
        if isinstance(request.stop, list):
            stop = stop_sequences + request.stop
        elif isinstance(request.stop, str):
            stop = stop_sequences + [request.stop]
        else:
            stop = stop_sequences
        logger.debug(f"Stop sequences:\n{stop}")

        # check if we can stream
        if request.stream is True and request.n > 1:
            raise ValueError("Cannot stream more than one completion")

        # construct body
        body = {
            "prompt": prompt,
            "max_tokens_to_sample": request.max_tokens,
            "temperature": request.temperature,
            "top_k": request.top_k,
            "top_p": request.top_p,
            "stop_sequences": stop,
            "anthropic_version": model_version_mapping[model],
        }
        logger.debug(f"Generation body:\n{body}")

        if request.stream:
            return stream_chat_request(client, body, model)
        else:
            choices = []
            generated_tokens = 0
            for _i in range(request.n):
                response = client.invoke_model(
                    body=json.dumps(body), modelId=model, accept="application/json", contentType="application/json"
                )
                # parse response
                res = json.loads(response.get("body").read())

                # convert to schema
                parsed = ChatCompletionResponseChoice(
                    index=_i,
                    message=ChatMessage(role="assistant", content=res["completion"].strip()),
                    finish_reason=res["stop_reason"],
                )
                generated_tokens += len(res["completion"].strip()) // 4
                choices.append(parsed)
                logger.debug(f"Response at index {_i}:\n{parsed}")
            # calculate usage details
            # TODO: fix when details is fixed
            prompt_tokens = int(len(prompt) / 4)
            total_tokens = prompt_tokens + generated_tokens

            return dump_object(
                ChatCompletionResponse(
                    model=request.model,
                    choices=choices,
                    usage=Usage(
                        prompt_tokens=prompt_tokens, completion_tokens=generated_tokens, total_tokens=total_tokens
                    ),
                )
            )

    @classmethod
    async def acreate(cls, *args, **kwargs):
        """
        Creates a new chat completion for the provided messages and parameters.
        """
        raise NotImplementedError("ChatCompletion.acreate is not implemented")

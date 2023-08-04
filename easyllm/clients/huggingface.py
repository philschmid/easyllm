import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from huggingface_hub import HfFolder, InferenceClient
from nanoid import generate
from easyllm.prompt_utils import PROMPT_MAPPING

from easyllm.prompt_utils.base import build_prompt, buildBasePrompt
from easyllm.schema.base import ChatMessage, Usage
from easyllm.schema.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    CompletionRequest,
    CompletionResponse,
    CompletionResponseChoice,
    CompletionResponseStreamChoice,
    CompletionStreamResponse,
    DeltaMessage,
    EmbeddingsObjectResponse,
    EmbeddingsRequest,
    EmbeddingsResponse,
)
from easyllm.utils import logger

# default parameters
api_type = "huggingface"
api_key = (
    os.environ.get(
        "HUGGINGFACE_TOKEN",
    )
    or HfFolder.get_token()
)
api_base = os.environ.get("HUGGINGFACE_API_BASE", None) or "https://api-inference.huggingface.co/models"
api_version = os.environ.get("HUGGINGFACE_API_VERSION", None) or "2023-07-29"
prompt_builder = os.environ.get("HUGGINGFACE_PROMPT", None)
stop_sequences = []
seed = 42


def stream_chat_request(client, prompt, stop, gen_kwargs, model):
    """Utility function for streaming chat requests."""
    id = f"hf-{generate(size=10)}"
    res = client.text_generation(
        prompt,
        stream=True,
        details=True,
        **gen_kwargs,
    )
    yield ChatCompletionStreamResponse(
        id=id,
        model=model,
        choices=[ChatCompletionResponseStreamChoice(index=0, delta=DeltaMessage(role="assistant"))],
    ).model_dump(exclude_none=True)
    # yield each generated token
    reason = None
    for _idx, chunk in enumerate(res):
        # skip special tokens
        if chunk.token.special:
            continue
        # stop if we encounter a stop sequence
        if chunk.token.text in stop:
            break
        # check if details is not none and if finish_reason key in details is not none
        if chunk.details is not None and chunk.details.finish_reason is not None:
            # set reason to finish reason
            reason = chunk.details.finish_reason
        # yield the generated token
        yield ChatCompletionStreamResponse(
            id=id,
            model=model,
            choices=[ChatCompletionResponseStreamChoice(index=0, delta=DeltaMessage(content=chunk.token.text))],
        ).model_dump(exclude_none=True)
    yield ChatCompletionStreamResponse(
        id=id,
        model=model,
        choices=[ChatCompletionResponseStreamChoice(index=0, finish_reason=reason, delta={})],
    ).model_dump(exclude_none=True)


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
If you want to use a custom prompt builder, set huggingface.prompt_builder to a function that takes a list of messages and returns a string.
You can also use existing prompt builders by importing them from easyllm.prompt_utils"""
            )
            prompt = buildBasePrompt(request.messages)
        else:
            prompt = build_prompt(request.messages, prompt_builder)

        # if the model is a url, use it directly
        if request.model:
            url = f"{api_base}/{request.model}"
            logger.debug(f"Url:\n{url}")
        else:
            url = api_base

        # create the client
        client = InferenceClient(url, token=api_key)

        # create stop sequences
        if isinstance(request.stop, list):
            stop = stop_sequences + request.stop
        if isinstance(request.stop, str):
            stop = stop_sequences + [request.stop]
        else:
            stop = stop_sequences
        logger.debug(f"Stop sequences:\n{stop}")

        # check if we can stream
        if request.stream is True and request.n > 1:
            raise ValueError("Cannot stream more than one completion")

        # create generation parameters
        if request.top_p == 0:
            request.top_p = 2e-4
        if request.top_p == 1:
            request.top_p = 0.9999999
        if request.temperature == 0:
            request.temperature = 2e-4

        gen_kwargs = {
            "do_sample": True,
            "return_full_text": False,
            "max_new_tokens": request.max_tokens,
            "top_p": float(request.top_p),
            "temperature": float(request.temperature),
            "stop_sequences": stop,
            "repetition_penalty": request.frequency_penalty,
            "top_k": request.top_k,
            "seed": seed,
        }
        logger.debug(f"Generation parameters:\n{gen_kwargs}")

        if request.stream:
            return stream_chat_request(client, prompt, stop, gen_kwargs, request.model)
        else:
            choices = []
            generated_tokens = 0
            for _i in range(request.n):
                res = client.text_generation(
                    prompt,
                    details=True,
                    **gen_kwargs,
                )
                parsed = ChatCompletionResponseChoice(
                    index=_i,
                    message=ChatMessage(role="assistant", content=res.generated_text),
                    finish_reason=res.details.finish_reason.value,
                )
                generated_tokens += res.details.generated_tokens
                choices.append(parsed)
                logger.debug(f"Response at index {_i}:\n{parsed}")
            # calculate usage details
            # TODO: fix when details is fixed
            prompt_tokens = int(len(prompt) / 4)
            total_tokens = prompt_tokens + generated_tokens

            return ChatCompletionResponse(
                model=request.model,
                choices=choices,
                usage=Usage(
                    prompt_tokens=prompt_tokens, completion_tokens=generated_tokens, total_tokens=total_tokens
                ),
            ).model_dump(exclude_none=True)

    @classmethod
    async def acreate(cls, *args, **kwargs):
        """
        Creates a new chat completion for the provided messages and parameters.
        """
        raise NotImplementedError("ChatCompletion.acreate is not implemented")


def stream_completion_request(client, prompt, stop, gen_kwargs, model):
    """Utility function for completion chat requests."""
    id = f"hf-{generate(size=10)}"
    res = client.text_generation(
        prompt,
        stream=True,
        details=True,
        **gen_kwargs,
    )
    # yield each generated token
    for _idx, chunk in enumerate(res):
        # skip special tokens
        if chunk.token.special:
            continue
        # stop if we encounter a stop sequence
        if chunk.token.text in stop:
            break
        # yield the generated token
        yield CompletionStreamResponse(
            id=id,
            model=model,
            choices=[CompletionResponseStreamChoice(index=0, text=chunk.token.text, logprobs=chunk.token.logprob)],
        ).model_dump(exclude_none=True)


class Completion:
    @staticmethod
    def create(
        prompt: Union[str, List[Any]],
        model: Optional[str] = None,
        suffix: Optional[str] = None,
        temperature: float = 0.9,
        top_p: float = 0.6,
        top_k: Optional[int] = 10,
        n: int = 1,
        max_tokens: int = 1024,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        frequency_penalty: Optional[float] = 1.0,
        logprobs: bool = False,
        echo: bool = False,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Creates a new completion for the provided prompt and parameters.

        Args:
            prompt (`Union[str, List[Any]]`) Text to use for the completion, if `prompt_builder` is set,
                prompt will be formatted with the `prompt_builder`.
            model (`str`, *optional*, defaults to None) The model to use for the completion. If not provided,
                defaults to the base url.
            suffix (`str`, *optional*, defaults to None) If defined, append this suffix to the prompt.
            temperature (`float`, defaults to 0.9): The temperature to use for the completion.
            top_p (`float`, defaults to 0.6): The top_p to use for the completion.
            top_k (`int`, *optional*, defaults to 10): The top_k to use for the completion.
            n (`int`, defaults to 1): The number of completions to generate.
            max_tokens (`int`, defaults to 1024): The maximum number of tokens to generate.
            stop (`List[str]`, *optional*, defaults to None): The stop sequence(s) to use for the completion.
            stream (`bool`, defaults to False): Whether to stream the completion.
            frequency_penalty (`float`, *optional*, defaults to 1.0): The frequency penalty to use for the completion.
            logprobs (`bool`, defaults to False) Weather to return logprobs.
            echo (`bool`, defaults to False) Whether to echo the prompt.
            debug (`bool`, defaults to False): Whether to enable debug logging.

        Tip: Prompt builder
            Make sure to always use a prompt builder for your model.
        """
        if debug:
            logger.setLevel(logging.DEBUG)

        request = CompletionRequest(
            model=model,
            prompt=prompt,
            suffix=suffix,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            n=n,
            max_tokens=max_tokens,
            stop=stop,
            stream=stream,
            frequency_penalty=frequency_penalty,
            logprobs=logprobs,
            echo=echo,
        )

        # include suffix if it exists
        if request.suffix is not None:
            request.prompt = request.prompt + request.suffix

        if prompt_builder is None:
            logging.warn(
                f"""huggingface.prompt_builder is not set.
Using default prompt builder for. Prompt sent to model will be:
----------------------------------------
{buildBasePrompt(request.prompt)}.
----------------------------------------
If you want to use a custom prompt builder, set huggingface.prompt_builder to a function that takes a list of messages and returns a string.
You can also use existing prompt builders by importing them from easyllm.prompt_utils"""
            )
            prompt = buildBasePrompt(request.prompt)
        else:
            prompt = build_prompt(request.messages, prompt_builder)
        logger.debug(f"Prompt sent to model will be:\n{prompt}")

        # if the model is a url, use it directly
        if request.model:
            url = f"{api_base}/{request.model}"
            logger.debug(f"Url:\n{url}")
        else:
            url = api_base

        # create the client
        client = InferenceClient(url, token=api_key)

        # create stop sequences
        if isinstance(request.stop, list):
            stop = stop_sequences + request.stop
        if isinstance(request.stop, str):
            stop = stop_sequences + [request.stop]
        else:
            stop = stop_sequences
        logger.debug(f"Stop sequences:\n{stop}")

        # check if we can stream
        if request.stream is True and request.n > 1:
            raise ValueError("Cannot stream more than one completion")

        # create generation parameters
        if request.top_p == 0:
            request.top_p = 2e-4
        if request.top_p == 1:
            request.top_p = 0.9999999
        if request.temperature == 0:
            request.temperature = 2e-4

        gen_kwargs = {
            "do_sample": True,
            "return_full_text": True if request.echo else False,
            "max_new_tokens": request.max_tokens,
            "top_p": float(request.top_p),
            "temperature": float(request.temperature),
            "stop_sequences": stop,
            "repetition_penalty": request.frequency_penalty,
            "top_k": request.top_k,
            "seed": seed,
        }
        logger.debug(f"Generation parameters:\n{gen_kwargs}")

        if request.stream:
            return stream_completion_request(client, prompt, stop, gen_kwargs, request.model)
        else:
            choices = []
            generated_tokens = 0
            for _i in range(request.n):
                res = client.text_generation(
                    prompt,
                    details=True,
                    **gen_kwargs,
                )
                parsed = CompletionResponseChoice(
                    index=_i,
                    text=res.generated_text,
                    finish_reason=res.details.finish_reason.value,
                )
                if request.logprobs:
                    parsed.logprobs = res.details.tokens

                generated_tokens += res.details.generated_tokens
                choices.append(parsed)
                logger.debug(f"Response at index {_i}:\n{parsed}")
            # calcuate usage details
            # TODO: fix when details is fixed
            prompt_tokens = int(len(prompt) / 4)
            total_tokens = prompt_tokens + generated_tokens

            return CompletionResponse(
                model=request.model,
                choices=choices,
                usage=Usage(
                    prompt_tokens=prompt_tokens, completion_tokens=generated_tokens, total_tokens=total_tokens
                ),
            ).model_dump(exclude_none=True)

    @classmethod
    async def acreate(cls, *args, **kwargs):
        """
        Creates a new chat completion for the provided messages and parameters.
        """
        raise NotImplementedError("ChatCompletion.acreate is not implemented")


class Embedding:
    @staticmethod
    def create(
        input: Union[str, List[Any]],
        model: Optional[str] = None,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Creates a new embeddings for the provided prompt and parameters.

        Args:
            input (`Union[str, List[Any]]`) document(s) to embed.
            model (`str`, *optional*, defaults to None) The model to use for the completion. If not provided,
                defaults to the base url.
            debug (`bool`, defaults to False): Whether to enable debug logging.

        Tip: Prompt builder
            Make sure to always use a prompt builder for your model.
        """
        if debug:
            logger.setLevel(logging.DEBUG)

        request = EmbeddingsRequest(model=model, input=input)

        # if the model is a url, use it directly
        if request.model:
            if api_base.endswith("/models"):
                url = f"{api_base.replace('/models', '/pipeline/feature-extraction')}/{request.model}"
            else:
                url = f"{api_base}/{request.model}"
            logger.debug(f"Url:\n{url}")
        else:
            url = api_base

        # create the client
        client = InferenceClient(url, token=api_key)

        # client is currently not supporting batched request thats why we run sequentially
        emb = []
        res = client.post(json={"inputs": request.input, "model": request.model, "task": "feature-extraction"})
        parsed_res = json.loads(res.decode())
        if isinstance(request.input, list):
            for idx, i in enumerate(parsed_res):
                emb.append(EmbeddingsObjectResponse(index=idx, embedding=i))
        else:
            emb.append(EmbeddingsObjectResponse(index=0, embedding=parsed_res))

        if isinstance(res, list):
            # TODO: only approximating tokens
            tokens = [int(len(i) / 4) for i in request.input]
        else:
            tokens = int(len(request.input) / 4)

        return EmbeddingsResponse(
            model=request.model,
            data=emb,
            usage=Usage(prompt_tokens=tokens, total_tokens=tokens),
        ).model_dump(exclude_none=True)

    @classmethod
    async def acreate(cls, *args, **kwargs):
        """
        Creates a new chat completion for the provided messages and parameters.
        """
        raise NotImplementedError("ChatCompletion.acreate is not implemented")

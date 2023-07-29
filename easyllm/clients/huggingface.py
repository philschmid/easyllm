import logging
import os
from typing import Any, Dict

from huggingface_hub import HfFolder, InferenceClient
from nanoid import generate

from easyllm.prompt_utils.base import buildBasePrompt
from easyllm.schema.base import ChatMessage, Usage
from easyllm.schema.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    DeltaMessage,
)
from easyllm.utils import logger

# default parameters
api_type = "huggingface"
api_key = os.getenv("HUGGINGFACE_TOKEN") or HfFolder.get_token()
api_base = os.getenv("HUGGINGFACE_API_BASE") or "https://api-inference.huggingface.co/models"
api_version = os.getenv("HUGGINGFACE_API_VERSION") or "2023-07-29"
prompt_builder = None
stop_sequences = []
seed = 42


def stream_request(client, prompt, stop, gen_kwargs, model):
    """Utility function for streaming requests."""
    id = f"hf-{generate(size=10)}"
    res = client.text_generation(
        prompt,
        stream=True,
        # TODO: fix when details is fixed
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
    def create(**kwargs) -> Dict[str, Any]:
        """
        Creates a new chat completion for the provided messages and parameters.
        Args:
            param1 (int): The first parameter.
            param2 (Optional[str]): The second parameter. Defaults to None.

        Tip: Prompt builder
            Make sure to always use a prompt builder for your model.
        """
        # deserialize the request
        debug = kwargs.pop("debug", False)
        if debug:
            logger.setLevel(logging.DEBUG)

        r = ChatCompletionRequest(**kwargs)

        if prompt_builder is None:
            logging.warn(
                f"""ChatCompletion.prompt_builder is not set.
Using default prompt builder for. Prompt sent to model will be:
----------------------------------------
{buildBasePrompt(r.messages)}.
----------------------------------------
If you want to use a custom prompt builder, set huggingface.prompt_builder to a function that takes a list of messages and returns a string.
You can also use existing prompt builders by importing them from easyllm.prompt_utils"""
            )
            prompt = buildBasePrompt(r.messages)
        else:
            prompt = prompt_builder(r.messages)
        logger.debug(f"Prompt sent to model will be:\n{prompt}")

        # if the model is a url, use it directly
        if r.model:
            url = f"{api_base}/{r.model}"
            logger.debug(f"Url:\n{url}")

        # create the client
        client = InferenceClient(url, token=api_key)

        # create stop sequences
        if isinstance(r.stop, list):
            stop = stop_sequences + r.stop
        if isinstance(r.stop, str):
            stop = stop_sequences + [r.stop]
        else:
            stop = stop_sequences
        logger.debug(f"Stop sequences:\n{stop}")

        # check if we can stream
        if r.stream is True and r.n > 1:
            raise ValueError("Cannot stream more than one completion")

        # create generation parameters
        if r.top_p == 0:
            r.top_p = 2e-4
        if r.top_p == 1:
            r.top_p = 0.9999999
        if r.temperature == 0:
            r.temperature = 2e-4

        gen_kwargs = {
            "do_sample": True,
            "return_full_text": False,
            "max_new_tokens": r.max_tokens,
            "top_p": float(r.top_p),
            "temperature": float(r.temperature),
            "stop_sequences": stop,
            "repetition_penalty": r.frequency_penalty,
            "top_k": r.top_k,
            "seed": seed,
        }
        logger.debug(f"Generation parameters:\n{gen_kwargs}")

        if r.stream:
            return stream_request(client, prompt, stop, gen_kwargs, r.model)
        else:
            choices = []
            generated_tokens = 0
            for _i in range(r.n):
                res = client.text_generation(
                    prompt,
                    # TODO: fix when details is fixed
                    details=False,
                    decoder_input_details=False,
                    **gen_kwargs,
                )
                parsed = ChatCompletionResponseChoice(
                    index=_i,
                    # TODO: fix when details is fixed
                    # message=ChatMessage(role="assistant", content=res.details.generated_text),
                    message=ChatMessage(role="assistant", content=res),
                    # TODO: fix when details is fixed
                    # finish_reason=res.details.finish_reason,
                )
                # TODO: fix when details is fixed
                # generated_tokens += res.details.generated_tokens
                generated_tokens = len(res)
                choices.append(parsed)
                logger.debug(f"Response at index {_i}:\n{parsed}")
            # calcuate usage details
            # prompt_tokens = len(res[0].details.prefill)
            # TODO: fix when details is fixed
            prompt_tokens = len(prompt)
            total_tokens = prompt_tokens + generated_tokens

            return ChatCompletionResponse(
                model=r.model,
                choices=choices,
                usage=Usage(
                    prompt_tokens=prompt_tokens, completion_tokens=generated_tokens, total_tokens=total_tokens
                ),
            ).model_dump()

    @classmethod
    async def acreate(cls, *args, **kwargs):
        """
        Creates a new chat completion for the provided messages and parameters.
        """
        raise NotImplementedError("ChatCompletion.acreate is not implemented")

# Clients

In the context of EasyLLM, a "client" refers to the code that interfaces with a particular LLM API, e.g. OpenAI.

Currently supported clients are:  

- `ChatCompletion` - ChatCompletion clients are used to interface with LLMs that are compatible with the OpenAI ChatCompletion API.


Currently supported clients are:  

- `huggingface.ChatCompletion` - a client for interfacing with HuggingFace models that are compatible with the OpenAI ChatCompletion API.

## `huggingface.ChatCompletion`

The `huggingface.ChatCompletion` client is used to interface with HuggingFace models running on Text Generation infernece that are compatible with the OpenAI ChatCompletion API. Checkout the [Examples](../examples/chat-completion-api) for more details and [How to stream completions](../examples/stream-chat-completion-api) for an example how to stream requests.


```python
from easyllm.clients import huggingface
from easyllm.prompt_utils import build_llama2_prompt

# The module automatically loads the HuggingFace API key from the environment variable HUGGINGFACE_TOKEN or from the HuggingFace CLI configuration file.
# huggingface.api_key="hf_xxx"

response = huggingface.ChatCompletion.create(
    model="meta-llama/Llama-2-70b-chat-hf",
    messages=[
        {"role": "system", "content": "\nYou are a helpful, respectful and honest assistant."},
        {"role": "user", "content": "Knock knock."},
    ],
      temperature=0.9,
      top_p=0.6,
      max_tokens=1024,
)
```


Supported parameters are:

* `model` - The model to use for the completion. If not provided, the defaults to base url.
* `messages` - `List[ChatMessage]` to use for the completion.
* `temperature` - The temperature to use for the completion. Defaults to 0.9.
* `top_p` - The top_p to use for the completion. Defaults to 0.6.
* `top_k` - The top_k to use for the completion. Defaults to 10.
* `n` - The number of completions to generate. Defaults to 1.
* `max_tokens` - The maximum number of tokens to generate. Defaults to 1024.
* `stop` - The stop sequence(s) to use for the completion. Defaults to None.
* `frequency_penalty` - The frequency penalty to use for the completion. Defaults to 1.0.
* `debug` - Whether to enable debug logging. Defaults to False.

### Setting HF token 

By default the `huggingface` client will try to read the `HUGGINGFACE_TOKEN` environment variable. If this is not set, it will try to read the token from the `~/.huggingface` folder. If this is not set, it will not use a token.

Alternatively you can set the token manually by setting `huggingface.api_key`.

```python
from easyllm.clients import huggingface

huggingface.api_key="hf_xxx"

res = huggingface.ChatCompletion.create(...)
```

### Changing url 

By default the `huggingface` client will try to read the `HUGGINGFACE_API_BASE` environment variable. If this is not set, it will use the default url `https://api-inference.huggingface.co/models`. This is helpful if you want to use a different url like `https://api-inference.huggingface.co/models` or a local url like `http://localhost:8000` or an Hugging Face Inference Endpoint.

Alternatively you can set the url manually by setting `huggingface.api_base`.


```python
from easyllm.clients import huggingface

huggingface.api_base="hf_xxx"

res = huggingface.ChatCompletion.create(...)
```

### Build Prompt

prompt_builder = None

By default the `huggingface` client has no `prompt_builder` set. If you want to use the `prompt_builder` you have to set it manually. If you don't set it, the client will use the default.

Checkout the [Prompt Utils](../prompt_utils) for more details.

```python
from easyllm.clients import huggingface
from easyllm.prompt_utils import build_llama2_prompt

huggingface.prompt_builder = build_llama2_prompt

res = huggingface.ChatCompletion.create(...)
```
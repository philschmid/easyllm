# Hugging Face 

EasyLLM provides a client for interfacing with HuggingFace models. The client is compatible with the [HuggingFace Inference API](https://huggingface.co/docs/api-inference/index), [Hugging Face Inference Endpoints](https://huggingface.co/docs/inference-endpoints/index) or any Web Service running [Text Generation Inference](https://github.com/huggingface/text-generation-inference) or compatible API endpoints. 

- `huggingface.ChatCompletion` - a client for interfacing with HuggingFace models that are compatible with the OpenAI ChatCompletion API.
- `huggingface.Completion` - a client for interfacing with HuggingFace models that are compatible with the OpenAI Completion API.
- `huggingface.Embedding` - a client for interfacing with HuggingFace models that are compatible with the OpenAI Embedding API.

## `huggingface.ChatCompletion`

The `huggingface.ChatCompletion` client is used to interface with HuggingFace models running on Text Generation inference that are compatible with the OpenAI ChatCompletion API. Checkout the [Examples](../examples/chat-completion-api) for more details and [How to stream completions](../examples/stream-chat-completion-api) for an example how to stream requests.


```python
from easyllm.clients import huggingface

# The module automatically loads the HuggingFace API key from the environment variable HUGGINGFACE_TOKEN or from the HuggingFace CLI configuration file.
# huggingface.api_key="hf_xxx"
hubbingface.prompt_builder = "llama2"

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

* `model` - The model to use for the completion. If not provided, defaults to the base url.
* `messages` - `List[ChatMessage]` to use for the completion.
* `temperature` - The temperature to use for the completion. Defaults to 0.9.
* `top_p` - The top_p to use for the completion. Defaults to 0.6.
* `top_k` - The top_k to use for the completion. Defaults to 10.
* `n` - The number of completions to generate. Defaults to 1.
* `max_tokens` - The maximum number of tokens to generate. Defaults to 1024.
* `stop` - The stop sequence(s) to use for the completion. Defaults to None.
* `stream` - Whether to stream the completion. Defaults to False.
* `frequency_penalty` - The frequency penalty to use for the completion. Defaults to 1.0.
* `debug` - Whether to enable debug logging. Defaults to False.

## `huggingface.Completion`

The `huggingface.Completion` client is used to interface with HuggingFace models running on Text Generation inference that are compatible with the OpenAI Completion API. Checkout the [Examples](../examples/text-completion-api) for more details and [How to stream completions](../examples/stream-text-completion-api) for an example how to stream requests.


```python
from easyllm.clients import huggingface

# The module automatically loads the HuggingFace API key from the environment variable HUGGINGFACE_TOKEN or from the HuggingFace CLI configuration file.
# huggingface.api_key="hf_xxx"
hubbingface.prompt_builder = "llama2"

response = huggingface.Completion.create(
    model="meta-llama/Llama-2-70b-chat-hf",
    prompt="What is the meaning of life?",
    temperature=0.9,
    top_p=0.6,
    max_tokens=1024,
)
```


Supported parameters are:

* `model` - The model to use for the completion. If not provided, defaults to the base url.
* `prompt` -  Text to use for the completion, if prompt_builder is set, prompt will be formatted with the prompt_builder.
* `temperature` - The temperature to use for the completion. Defaults to 0.9.
* `top_p` - The top_p to use for the completion. Defaults to 0.6.
* `top_k` - The top_k to use for the completion. Defaults to 10.
* `n` - The number of completions to generate. Defaults to 1.
* `max_tokens` - The maximum number of tokens to generate. Defaults to 1024.
* `stop` - The stop sequence(s) to use for the completion. Defaults to None.
* `stream` - Whether to stream the completion. Defaults to False.
* `frequency_penalty` - The frequency penalty to use for the completion. Defaults to 1.0.
* `debug` - Whether to enable debug logging. Defaults to False.
* `echo` - Whether to echo the prompt. Defaults to False.
* `logprobs` - Weather to return logprobs. Defaults to None.


## `huggingface.Embedding`

The `huggingface.Embedding` client is used to interface with HuggingFace models running as an API that are compatible with the OpenAI Embedding API. Checkout the [Examples](../examples/get-embeddings) for more details.

```python
from easyllm.clients import huggingface

# The module automatically loads the HuggingFace API key from the environment variable HUGGINGFACE_TOKEN or from the HuggingFace CLI configuration file.
# huggingface.api_key="hf_xxx"

embedding = huggingface.Embedding.create(
    model="sentence-transformers/all-MiniLM-L6-v2",
    text="What is the meaning of life?",
)

len(embedding["data"][0]["embedding"])
```

Supported parameters are:

* `model` - The model to use to create the embedding. If not provided, defaults to the base url.
* `input` -  `Union[str, List[str]]` document(s) to embed.


## Environment Configuration

You can configure the `huggingface` client by setting environment variables or overwriting the default values. See below on how to adjust the HF token, url and prompt builder.

### Setting HF token 

By default the `huggingface` client will try to read the `HUGGINGFACE_TOKEN` environment variable. If this is not set, it will try to read the token from the `~/.huggingface` folder. If this is not set, it will not use a token.

Alternatively you can set the token manually by setting `huggingface.api_key`.


manually setting the api key:

```python
from easyllm.clients import huggingface

huggingface.api_key="hf_xxx"

res = huggingface.ChatCompletion.create(...)
```

Using environment variable:

```python
# can happen elsehwere
import os
os.environ["HUGGINGFACE_TOKEN"] = "hf_xxx"

from easyllm.clients import huggingface
```


### Changing url 

By default the `huggingface` client will try to read the `HUGGINGFACE_API_BASE` environment variable. If this is not set, it will use the default url `https://api-inference.huggingface.co/models`. This is helpful if you want to use a different url like `https://zj5lt7pmzqzbp0d1.us-east-1.aws.endpoints.huggingface.cloud` or a local url like `http://localhost:8000` or an Hugging Face Inference Endpoint.

Alternatively you can set the url manually by setting `huggingface.api_base`. If you set a custom you have to leave the `model` parameter empty. 

manually setting the api base:

```python
from easyllm.clients import huggingface

huggingface.api_base="https://my-url"


res = huggingface.ChatCompletion.create(...)
```

Using environment variable:

```python
# can happen elsehwere
import os
os.environ["HUGGINGFACE_API_BASE"] = "https://my-url"

from easyllm.clients import huggingface
```




### Build Prompt

By default the `huggingface` client will try to read the `HUGGINGFACE_PROMPT` environment variable and tries to map the value to the `PROMPT_MAPPING` dictionary. If this is not set, it will use the default prompt builder. 
You can also set it manually.

Checkout the [Prompt Utils](../prompt_utils) for more details.


manually setting the prompt builder:

```python
from easyllm.clients import huggingface

huggingface.prompt_builder = "llama2"

res = huggingface.ChatCompletion.create(...)
```

Using environment variable:

```python
# can happen elsehwere
import os
os.environ["HUGGINGFACE_PROMPT"] = "llama2"

from easyllm.clients import huggingface
```
# Amazon SageMaker

EasyLLM provides a client for interfacing with Amazon SageMaker models. 

- `sagemaker.ChatCompletion` - a client for interfacing with sagemaker models that are compatible with the OpenAI ChatCompletion API.
- `sagemaker.Completion` - a client for interfacing with sagemaker models that are compatible with the OpenAI Completion API.
- `sagemaker.Embedding` - a client for interfacing with sagemaker models that are compatible with the OpenAI Embedding API.

## `sagemaker.ChatCompletion`

The `sagemaker.ChatCompletion` client is used to interface with sagemaker models running on Text Generation inference that are compatible with the OpenAI ChatCompletion API. Checkout the [Examples](../examples/sagemaker-chat-completion-api)


```python
import os 
from easyllm.clients import sagemaker

# set env for prompt builder
os.environ["HUGGINGFACE_PROMPT"] = "llama2" # vicuna, wizardlm, stablebeluga, open_assistant
os.environ["AWS_REGION"] = "us-east-1"  # change to your region
# os.environ["AWS_ACCESS_KEY_ID"] = "XXX" # needed if not using boto3 session
# os.environ["AWS_SECRET_ACCESS_KEY"] = "XXX" # needed if not using boto3 session


response = sagemaker.ChatCompletion.create(
    model="huggingface-pytorch-tgi-inference-2023-08-08-14-15-52-703",
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

## `sagemaker.Completion`

The `sagemaker.Completion` client is used to interface with sagemaker models running on Text Generation inference that are compatible with the OpenAI Completion API. Checkout the [Examples](../examples/sagemaker-text-completion-api).


```python
import os 
from easyllm.clients import sagemaker

# set env for prompt builder
os.environ["HUGGINGFACE_PROMPT"] = "llama2" # vicuna, wizardlm, stablebeluga, open_assistant
os.environ["AWS_REGION"] = "us-east-1"  # change to your region
# os.environ["AWS_ACCESS_KEY_ID"] = "XXX" # needed if not using boto3 session
# os.environ["AWS_SECRET_ACCESS_KEY"] = "XXX" # needed if not using boto3 session

response = sagemaker.Completion.create(
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


## `sagemaker.Embedding`

The `sagemaker.Embedding` client is used to interface with sagemaker models running as an API that are compatible with the OpenAI Embedding API. Checkout the [Examples](../examples/sagemaker-get-embeddings) for more details.

```python
import os 
# set env for prompt builder
os.environ["HUGGINGFACE_PROMPT"] = "llama2" # vicuna, wizardlm, stablebeluga, open_assistant
os.environ["AWS_REGION"] = "us-east-1"  # change to your region
# os.environ["AWS_ACCESS_KEY_ID"] = "XXX" # needed if not using boto3 session
# os.environ["AWS_SECRET_ACCESS_KEY"] = "XXX" # needed if not using boto3 session

from easyllm.clients import sagemaker

embedding = sagemaker.Embedding.create(
    model="SageMakerModelEmbeddingEndpoint24E49D09-64prhjuiWUtE",
    input="That's a nice car.",
)

len(embedding["data"][0]["embedding"])
```

Supported parameters are:

* `model` - The model to use to create the embedding. If not provided, defaults to the base url.
* `input` -  `Union[str, List[str]]` document(s) to embed.


## Environment Configuration

You can configure the `sagemaker` client by setting environment variables or overwriting the default values. See below on how to adjust the HF token, url and prompt builder.

### Setting Credentials

By default the `sagemaker` client will try to read the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variable. If this is not set, it will try to use `boto3`. 

Alternatively you can set the token manually by setting `sagemaker.*`.

manually setting the api key:

```python
from easyllm.clients import sagemaker

sagemaker.api_aws_access_key="xxx"
sagemaker.api_aws_secret_key="xxx"

res = sagemaker.ChatCompletion.create(...)
```

Using environment variable:

```python
# can happen elsehwere
import os
os.environ["AWS_ACCESS_KEY_ID"] = "xxx"
os.environ["AWS_SECRET_ACCESS_KEY"] = "xxx"

from easyllm.clients import sagemaker
```


### Build Prompt

By default the `sagemaker` client will try to read the `sagemaker_PROMPT` environment variable and tries to map the value to the `PROMPT_MAPPING` dictionary. If this is not set, it will use the default prompt builder. 
You can also set it manually.

Checkout the [Prompt Utils](../prompt_utils) for more details.


manually setting the prompt builder:

```python
from easyllm.clients import sagemaker

sagemaker.prompt_builder = "llama2"

res = sagemaker.ChatCompletion.create(...)
```

Using environment variable:

```python
# can happen elsehwere
import os
os.environ["HUGGINGFACE_PROMPT"] = "llama2"

from easyllm.clients import sagemaker
```
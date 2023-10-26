# Amazon Bedrock

EasyLLM provides a client for interfacing with Amazon Bedrock models. 

- `bedrock.ChatCompletion` - a client for interfacing with Bedrock models that are compatible with the OpenAI ChatCompletion API.
- `bedrock.Completion` - a client for interfacing with Bedrock models that are compatible with the OpenAI Completion API.
- `bedrock.Embedding` - a client for interfacing with Bedrock models that are compatible with the OpenAI Embedding API.

## `bedrock.ChatCompletion`

The `bedrock.ChatCompletion` client is used to interface with Bedrock models running on Text Generation inference that are compatible with the OpenAI ChatCompletion API. Checkout the [Examples](../examples/bedrock-chat-completion-api)


```python
import os 
# set env for prompt builder
os.environ["BEDROCK_PROMPT"] = "anthropic" # vicuna, wizardlm, stablebeluga, open_assistant
os.environ["AWS_REGION"] = "us-east-1"  # change to your region
# os.environ["AWS_ACCESS_KEY_ID"] = "XXX" # needed if not using boto3 session
# os.environ["AWS_SECRET_ACCESS_KEY"] = "XXX" # needed if not using boto3 session

from easyllm.clients import bedrock

response = bedrock.ChatCompletion.create(
    model="anthropic.claude-v2",
    messages=[
        {"role": "user", "content": "What is 2 + 2?"},
    ],
      temperature=0.9,
      top_p=0.6,
      max_tokens=1024,
      debug=False,
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
* `debug` - Whether to enable debug logging. Defaults to False.


### Build Prompt

By default the `bedrock` client will try to read the `BEDROCK_PROMPT` environment variable and tries to map the value to the `PROMPT_MAPPING` dictionary. If this is not set, it will use the default prompt builder. 
You can also set it manually.

Checkout the [Prompt Utils](../prompt_utils) for more details.


manually setting the prompt builder:

```python
from easyllm.clients import bedrock

bedrock.prompt_builder = "anthropic"

res = bedrock.ChatCompletion.create(...)
```

Using environment variable:

```python
# can happen elsehwere
import os
os.environ["BEDROCK_PROMPT"] = "anthropic"

from easyllm.clients import bedrock
```
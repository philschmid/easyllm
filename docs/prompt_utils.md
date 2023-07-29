# Prompt utilities

The `prompt_utils`  module contains functions to assist with converting Message's Dictonaries into prompts that can be used with `ChatCompletion` clients. 

## Llama 2 Chat builder 

Uses LLama 2 chat tokens (`[INST]`) to create a prompt, learn more in the [Hugging Face Blog on how to prompt Llama 2](https://huggingface.co/blog/llama2#how-to-prompt-llama-2). If a `Message` with an unsupported `role` is passed, an error will be thrown.

```python
from easyllm.prompt_utils import build_llama2_prompt

messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain asynchronous programming in the style of the pirate Blackbeard."},
]
prompt = build_llama2_prompt(messages)
```

### set prompt builder for client

```python
from easyllm.clients import huggingface
from easyllm.prompt_utils import build_llama2_prompt

huggingface.prompt_builder = build_llama2_prompt
```
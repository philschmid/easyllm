# Prompt utilities

The `prompt_utils`  module contains functions to assist with converting Message's Dictionaries into prompts that can be used with `ChatCompletion` clients. 

## Set prompt builder for client

```python
from easyllm.clients import huggingface
from easyllm.prompt_utils import build_llama2_prompt

huggingface.prompt_builder = build_llama2_prompt
```

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




## Vicuna Chat builder 

Builds a Vicuna prompt for a chat conversation as defined in the [fastchat repository](https://github.com/lm-sys/FastChat/blob/main/docs/vicuna_weights_version.md#prompt-template)
. If a `Message` with an unsupported `role` is passed, an error will be thrown.

```python
from easyllm.prompt_utils import build_vicuna_prompt

messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain asynchronous programming in the style of the pirate Blackbeard."},
]
prompt = build_vicuna_prompt(messages)
```

## Hugging Face ChatML builder 

Builds a Hugging Face ChatML prompt for a chat conversation. The Hugging Face ChatML has different prompts for different models, e.g. StarChat or Falcon. If a `Message` with an unsupported `role` is passed, an error will be thrown.

### StarChat

```python
from easyllm.prompt_utils import build_chatml_starchat_prompt

messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain asynchronous programming in the style of the pirate Blackbeard."},
]
prompt = build_chatml_starchat_prompt(messages)
```

### Falcon

```python
from easyllm.prompt_utils import build_chatml_falcon_prompt

messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain asynchronous programming in the style of the pirate Blackbeard."},
]
prompt = build_chatml_falcon_prompt(messages)
```


## WizardLM Chat builder 

Builds a WizardLM prompt for a chat conversation as defined in the [WizardLM repository](https://github.com/nlpxucan/WizardLM/blob/main/WizardLM/src/infer_wizardlm13b.py#L79)
. If a `Message` with an unsupported `role` is passed, an error will be thrown.

```python
from easyllm.prompt_utils import build_wizardlm_prompt

messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain asynchronous programming in the style of the pirate Blackbeard."},
]
prompt = build_wizardlm_prompt(messages)
```
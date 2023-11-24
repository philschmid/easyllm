# Clients

In the context of EasyLLM, a "client" refers to the code that interfaces with a particular LLM API, e.g. OpenAI.

Currently supported clients are:  

- `ChatCompletion` - ChatCompletion clients are used to interface with LLMs that are compatible with the OpenAI ChatCompletion API.
- `Completion` - Completion clients are used to interface with LLMs that are compatible with the OpenAI Completion API.
- `Embedding` - Embedding clients are used to interface with LLMs that are compatible with the OpenAI Embedding API.

Currently supported clients are:  

## Hugging Face

- [huggingface.ChatCompletion](huggingface/#huggingfacechatcompletion) - a client for interfacing with HuggingFace models that are compatible with the OpenAI ChatCompletion API.
- [huggingface.Completion](huggingface/#huggingfacechatcompletion) - a client for interfacing with HuggingFace models that are compatible with the OpenAI Completion API.
- [huggingface.Embedding](huggingface/#huggingfacechatcompletion) - a client for interfacing with HuggingFace models that are compatible with the OpenAI Embedding API.

## Amazon SageMaker

- [sagemaker.ChatCompletion](sagemaker/#sagemakerchatcompletion) - a client for interfacing with Amazon SageMaker models that are compatible with the OpenAI ChatCompletion API.
- [sagemaker.Completion](sagemaker/#sagemakercompletion) - a client for interfacing with Amazon SageMaker models that are compatible with the OpenAI Completion API.
- [sagemaker.Embedding](sagemaker/#sagemakerembedding) - a client for interfacing with Amazon SageMaker models that are compatible with the OpenAI Embedding API.

## Amazon Bedrock

- [bedrock.ChatCompletion](bedrock/#bedrockchatcompletion) - a client for interfacing with Amazon Bedrock models that are compatible with the OpenAI ChatCompletion API.

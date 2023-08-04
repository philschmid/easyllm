from .chatml_hf import (
    build_chatml_falcon_prompt,
    build_chatml_starchat_prompt,
    chatml_falcon_stop_sequences,
    chatml_starchat_stop_sequences,
)
from .llama2 import build_llama2_prompt, llama2_stop_sequences
from .open_assistant import build_open_assistant_prompt, open_assistant_stop_sequences
from .stablebeluga import build_stablebeluga_prompt, stablebeluga_stop_sequences
from .vicuna import build_vicuna_prompt, vicuna_stop_sequences
from .wizardlm import build_wizardlm_prompt, wizardlm_stop_sequences

PROMPT_MAPPING = {
    "chatml_falcon": build_chatml_falcon_prompt,
    "chatml_starchat": build_chatml_starchat_prompt,
    "llama2": build_llama2_prompt,
    "open_assistant": build_open_assistant_prompt,
    "stablebeluga": build_stablebeluga_prompt,
    "vicuna": build_vicuna_prompt,
    "wizardlm": build_wizardlm_prompt,
}

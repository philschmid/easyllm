import importlib.util
import re
import unicodedata
from typing import Dict

from huggingface_hub import hf_hub_download
from pydantic import BaseModel, ConfigDict

_kenlm = importlib.util.find_spec("kenlm") is not None
_sentencepiece = importlib.util.find_spec("sentencepiece") is not None

if _kenlm or not _sentencepiece:
    import kenlm
    import sentencepiece


class SentencePiece:
    def __init__(
        self,
        model: str,
    ):
        super().__init__()
        self.sp = sentencepiece.SentencePieceProcessor()
        self.sp.load(str(model))

    def do(self, text: dict) -> dict:
        tokenized = self.sp.encode_as_pieces(text)
        return " ".join(tokenized)


class KenlmModel:
    digit_re: re.Pattern[str] = re.compile(r"\d")
    unicode_punct: Dict[str, str] = {
        "，": ",",
        "。": ".",
        "、": ",",
        "„": '"',
        "”": '"',
        "“": '"',
        "«": '"',
        "»": '"',
        "１": '"',
        "」": '"',
        "「": '"',
        "《": '"',
        "》": '"',
        "´": "'",
        "∶": ":",
        "：": ":",
        "？": "?",
        "！": "!",
        "（": "(",
        "）": ")",
        "；": ";",
        "–": "-",
        "—": " - ",
        "．": ". ",
        "～": "~",
        "’": "'",
        "…": "...",
        "━": "-",
        "〈": "<",
        "〉": ">",
        "【": "[",
        "】": "]",
        "％": "%",
        "►": "-",
    }
    unicode_punct_re: re.Pattern = re.compile(f"[{''.join(unicode_punct.keys())}]")
    non_printing_chars_re: re.Pattern = re.compile(f"[{''.join(map(chr, list(range(0,32)) + list(range(127,160))))}]")
    model: kenlm.Model = None
    tokenizer: SentencePiece = None
    accent: bool = False
    case: bool = False
    numbers: bool = True
    punct: int = 1

    def __init__(
        self,
        model_path: str,
        tokenizer_path: str,
        lower_case: bool = False,
        remove_accents: bool = False,
        normalize_numbers: bool = True,
        punctuation: int = 1,
    ):
        self.model = kenlm.Model(model_path)
        self.tokenizer = SentencePiece(tokenizer_path)
        self.accent = remove_accents
        self.case = lower_case
        self.numbers = normalize_numbers
        self.punct = punctuation

    @classmethod
    def from_pretrained(
        cls,
        language_or_path: str,
    ):
        try:
            model = hf_hub_download("philschmid/kenlm", filename=f"wikipedia/{language_or_path}.arpa.bin")
            tokenizer = hf_hub_download("philschmid/kenlm", filename=f"wikipedia/{language_or_path}.sp.model")
        except Exception:
            raise ValueError(
                f"KenLM model for {language_or_path} not found at https://huggingface.co/philschmid/kenlm. Please train your own model and upload it to the hub."
            ) from None

        return cls(
            model,
            tokenizer,
            False,
            False,
            True,
            1,
        )

    def pp(self, log_score, length):
        return 10.0 ** (-log_score / length)

    def get_perplexity(self, doc: str, normalize_cc_net: bool = True):
        if normalize_cc_net:
            doc = self.normalize(
                doc,
                accent=self.accent,
                case=self.case,
                numbers=self.numbers,
                punct=self.punct,
            )
        # Tokenize (after normalizing): See https://github.com/facebookresearch/cc_net/blob/bda555bd1cf1ee2e0b925363e62a61cd46c8b60d/cc_net/mine.py#L352 for full pipeline
        doc = self.tokenizer.do(doc)
        doc_log_score, doc_length = 0, 0
        for line in doc.split("\n"):
            log_score = self.model.score(line)
            length = len(line.split()) + 1
            doc_log_score += log_score
            doc_length += length
        return round(self.pp(doc_log_score, doc_length), 1)

    def normalize(
        self,
        line: str,
        accent: bool = True,
        case: bool = True,
        numbers: bool = True,
        punct: int = 1,
    ) -> str:
        line = line.strip()
        if not line:
            return line
        if case:
            line = line.lower()
        if accent:
            line = self.strip_accents(line)
        if numbers:
            line = self.digit_re.sub("0", line)
        if punct == 1:
            line = self.replace_unicode_punct(line)
        elif punct == 2:
            line = self.remove_unicode_punct(line)
        line = self.remove_non_printing_char(line)
        return line

    def strip_accents(self, line: str) -> str:
        """Strips accents from a piece of text."""
        nfd = unicodedata.normalize("NFD", line)
        output = [c for c in nfd if unicodedata.category(c) != "Mn"]
        if len(output) == line:
            return line
        return "".join(output)

    def replace_unicode_punct(self, text: str) -> str:
        return "".join(self.unicode_punct.get(c, c) for c in text)

    def remove_unicode_punct(self, text: str) -> str:
        """More aggressive version of replace_unicode_punct but also faster."""
        return self.unicode_punct_re.sub("", text)

    def remove_non_printing_char(self, text: str) -> str:
        return self.non_printing_chars_re.sub("", text)


class PerplexityFilter(BaseModel):
    model: KenlmModel = None
    min_threshold: int = 0
    max_threshold: int = 1000
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, language: str, min_threshold: int = 0, max_threshold: int = 1000):
        super().__init__()
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.model = KenlmModel.from_pretrained(language)

    def __call__(self, doc: str) -> bool:
        # returns True if the perplexity of the document outside of the threshold,
        # meaning smaller than min_threshold or larger than max_threshold
        perplexity = self.model.get_perplexity(doc)
        if perplexity < self.min_threshold or perplexity > self.max_threshold:
            return True
        # otherwise keep
        return False

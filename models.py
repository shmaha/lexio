# ============================================================
# models.py -- Request and response data shapes
# ============================================================
# Pydantic models define the contract of your API.
# FastAPI uses these to validate inputs and outputs
# automatically -- no manual checking needed.
# ============================================================

from pydantic import BaseModel, Field, field_validator
from config import MAX_WORD_LENGTH, MIN_WORD_LENGTH, SUPPORTED_LANGUAGES
import re

# --- Request model ---
class TranslationRequest(BaseModel):
    word: str = Field(
        min_length=MIN_WORD_LENGTH,
        max_length=MAX_WORD_LENGTH,
        description="A single French word to translate"
    )
    language: str = Field(
        description=f"Language of the word. Supported: {SUPPORTED_LANGUAGES}"
    )

    @field_validator("word")
    @classmethod
    def check_no_injection(cls, v):
        # Layer 1 defence -- catches obvious attempts only.
        # Not a complete solution. Structural separation in
        # the prompt architecture is the more meaningful defence.
        injection_patterns = [
            "ignore", "forget", "disregard",
            "you are now", "act as", "pretend",
            "system:", "assistant:", "instructions:"
        ]
        lower = v.lower()
        for pattern in injection_patterns:
            if pattern in lower:
                raise ValueError("Invalid input")
        return v.strip()


# --- Sentence example model ---
class SentenceExample(BaseModel):
    original: str
    english: str
    situation: str


# --- Response model ---
class TranslationResponse(BaseModel):
    word: str
    translation: str
    part_of_speech: str
    synonyms: list[str]
    antonyms: list[str]
    cultural_context: str
    sentence_examples: list[SentenceExample]
    provider: str  # tells you which model answered
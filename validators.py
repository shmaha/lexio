# ============================================================
# validators.py -- Input validation beyond Pydantic
# ============================================================
# Pydantic handles type and length validation automatically.
# This file handles semantic validation -- is the input
# actually a French word, not just a valid string?
# ============================================================

from fastapi import HTTPException, status
from config import SUPPORTED_LANGUAGES
import re

def check_injection(v: str) -> str:
    """
    Shared prompt injection check.
    Used by both DictionaryRequest and TranslateRequest.
    """
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


def check_supported_language(v: str) -> str:
    """
    Shared language validation.
    Used by both DictionaryRequest and TranslateRequest.
    """
    if v not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{v}'. "
            f"Supported: {SUPPORTED_LANGUAGES}"
        )
    return v


def validate_single_word(word: str) -> str:
    word = word.strip()
    pattern = r"^[\w\-\']+$"
    if not re.match(pattern, word, re.UNICODE):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Input must be a single word. "
                   "Numbers, sentences and special characters are not accepted."
        )
    if " " in word:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please enter a single word, not a phrase or sentence."
        )
    return word


def validate_provider(provider: str) -> str:
    from config import SUPPORTED_PROVIDERS
    if provider.lower() not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider '{provider}'. "
                   f"Supported values: {SUPPORTED_PROVIDERS}"
        )
    return provider.lower()
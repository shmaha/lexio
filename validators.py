# ============================================================
# validators.py -- Input validation beyond Pydantic
# ============================================================
# Pydantic handles type and length validation automatically.
# This file handles semantic validation -- is the input
# actually a French word, not just a valid string?
# ============================================================

import re
from fastapi import HTTPException, status


def validate_single_word(word: str) -> str:
    """
    Validates input is a single word across any supported language.
    Covers Latin, Cyrillic, Arabic, CJK, Devanagari and more.
    """
    word = word.strip()

    # Unicode-aware pattern covering all major writing systems
    # \w matches word characters in any language when using re.UNICODE
    # We also allow hyphens and apostrophes for compound words
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
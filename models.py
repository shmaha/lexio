# ============================================================
# models.py -- Request and response data shapes
# ============================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from config import (
    MAX_WORD_LENGTH, MIN_WORD_LENGTH,
    SUPPORTED_LANGUAGES,
    DEFAULT_DICTIONARY_SOURCE_LANGUAGE,
    DEFAULT_DICTIONARY_TARGET_LANGUAGE,
    DEFAULT_TRANSLATE_SOURCE_LANGUAGE,
    DEFAULT_TRANSLATE_TARGET_LANGUAGE
)
from validators import check_injection, check_supported_language


# ============================================================
# DICTIONARY -- deep linguistic analysis, single words only
# ============================================================

class DictionaryRequest(BaseModel):
    word: str = Field(
        min_length=MIN_WORD_LENGTH,
        max_length=MAX_WORD_LENGTH,
        description="A single word to analyse"
    )
    source_language: str = Field(
        default=DEFAULT_DICTIONARY_SOURCE_LANGUAGE,
        description=f"Language of the word. Supported: {SUPPORTED_LANGUAGES}"
    )
    target_language: str = Field(
        default=DEFAULT_DICTIONARY_TARGET_LANGUAGE,
        description=f"Language for translations and explanations. Supported: {SUPPORTED_LANGUAGES}"
    )

    @field_validator("source_language", "target_language")
    @classmethod
    def validate_language(cls, v):
        return check_supported_language(v)

    @field_validator("word")
    @classmethod
    def validate_injection(cls, v):
        return check_injection(v)


class SentenceExample(BaseModel):
    original: str
    translation: str
    situation: str
    tense_or_form: Optional[str]


class Usage(BaseModel):
    part_of_speech_notes: str
    forms: dict[str, str]
    sentence_examples: list[SentenceExample]


class WordDefinition(BaseModel):
    part_of_speech: str
    translation: str
    synonyms: list[str]
    antonyms: list[str]
    usage: Usage
    cultural_context: str


class DictionaryResponse(BaseModel):
    word: str
    source_language: str
    target_language: str
    definitions: list[WordDefinition]
    provider: str


# ============================================================
# TRANSLATE -- practical communication, words and phrases
# ============================================================

class TranslateRequest(BaseModel):
    input: str = Field(
        min_length=1,
        max_length=150,
        description="A word or phrase to translate"
    )
    source_language: str = Field(
        default=DEFAULT_TRANSLATE_SOURCE_LANGUAGE,
        description=f"Source language. Supported: {SUPPORTED_LANGUAGES}"
    )
    target_language: str = Field(
        default=DEFAULT_TRANSLATE_TARGET_LANGUAGE,
        description=f"Target language. Supported: {SUPPORTED_LANGUAGES}"
    )
    intent: str = Field(default="say", description="heard or say")

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, v):
        if v not in ["heard", "say"]:
            raise ValueError("Intent must be 'heard' or 'say'")
        return v

    @field_validator("source_language", "target_language")
    @classmethod
    def validate_language(cls, v):
        return check_supported_language(v)

    @field_validator("input")
    @classmethod
    def validate_injection(cls, v):
        return check_injection(v)


class TranslateVariant(BaseModel):
    style: str
    translation: str
    notes: str


class TranslateResponse(BaseModel):
    input: str
    source_language: str
    target_language: str
    literal_meaning: Optional[str]
    fun_fact: Optional[str]
    usage_warning: Optional[str]
    variants: list[TranslateVariant]
    provider: str
# ============================================================
# main.py -- French Ami API v2
# ============================================================

from fastapi import FastAPI, Depends, Header, HTTPException
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

from models import TranslationRequest, TranslationResponse, SentenceExample
from prompts import build_messages
from providers import get_provider
from validators import validate_single_word, validate_provider
from auth import verify_api_key
from config import DEFAULT_MODEL_PROVIDER, DEFAULT_LANGUAGE

load_dotenv()

app = FastAPI(
    title="French Ami API",
    version="2.0.0",
    description="Learn French vocabulary deeply -- translation, "
                "synonyms, antonyms, cultural context and usage examples."
)


# ============================================================
# V1 -- DEPRECATED
# Will be removed in v3. Use /v2/translate instead.
# No auth, no provider switching, basic response only.
# ============================================================

_v1_client = OpenAI()

_v1_system_prompt = """You are a French language expert.
When given a French word, return a JSON object with exactly these fields:
- translation: English translation of the word
- synonyms: list of 3-5 French synonyms
- antonyms: list of 2-3 French antonyms (empty list if none exist)
- cultural_context: 2-3 sentences explaining the cultural significance

Return only valid JSON, no markdown, no explanation."""


@app.post(
    "/v1/translate",
    deprecated=True,
    tags=["v1 -- Deprecated"],
    summary="Translate a French word (deprecated -- use /v2/translate)"
)
async def translate_word_v1(request: TranslationRequest):
    response = _v1_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _v1_system_prompt},
            {"role": "user", "content": request.word}
        ]
    )
    result = json.loads(response.choices[0].message.content)
    return {
        "word": request.word,
        "translation": result["translation"],
        "synonyms": result["synonyms"],
        "antonyms": result["antonyms"],
        "cultural_context": result["cultural_context"],
        "_warning": "This endpoint is deprecated and will be removed in v3. "
                    "Please migrate to /v2/translate."
    }


# ============================================================
# V2 -- CURRENT
# ============================================================

@app.post(
    "/v2/translate",
    response_model=TranslationResponse,
    tags=["v2 -- Current"],
    dependencies=[Depends(verify_api_key)]
)
async def translate_word(
    request: TranslationRequest,
    x_model_provider: Optional[str] = Header(
        default=None,
        description="Override model provider: 'openai' or 'gemini'"
    )
):
    # Step 1 -- validate and clean the word
    word = validate_single_word(request.word)

    # Step 2 -- determine which provider to use
    provider_name = DEFAULT_MODEL_PROVIDER
    if x_model_provider:
        provider_name = validate_provider(x_model_provider)

    # Step 3 -- get the provider instance
    provider = get_provider(provider_name)

    # Step 4 -- build the messages and call the model
    language = request.language if request.language else DEFAULT_LANGUAGE
    messages = build_messages(word, language)
    result = provider.complete(messages)

    # Step 5 -- handle error response from model
    if result.get("error"):
        raise HTTPException(
            status_code=422,
            detail=result.get("translation", "Unknown error from model")
        )

    # Step 6 -- build and return the response
    return TranslationResponse(
    word=word,
    translation=result["translation"],
    part_of_speech=result["part_of_speech"],
    synonyms=result["synonyms"],
    antonyms=result["antonyms"],
    cultural_context=result["cultural_context"],
    sentence_examples=[
        SentenceExample(
            original=ex["original"],
            english=ex["english"],
            situation=ex["situation"]
        )
        for ex in result["sentence_examples"]
    ],
    provider=provider.provider_name
)


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "default_provider": DEFAULT_MODEL_PROVIDER
    }
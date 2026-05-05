# ============================================================
# main.py -- Lexio API v3
# ============================================================
# Endpoints:
#   POST /dictionary -- deep linguistic analysis, single words
#   POST /translate  -- practical communication, words and phrases
#   GET  /health     -- system status
# ============================================================

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.openapi.utils import get_openapi
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from models import (
    DictionaryRequest, DictionaryResponse,
    TranslateRequest, TranslateResponse,
    SentenceExample, Usage, WordDefinition,
    TranslateVariant
)
from prompts import build_dictionary_messages, build_translate_messages
from providers import get_provider
from validators import validate_single_word, validate_provider
from auth import verify_api_key
from config import (
    DEFAULT_MODEL_PROVIDER,
    DEFAULT_DICTIONARY_SOURCE_LANGUAGE,
    DEFAULT_DICTIONARY_TARGET_LANGUAGE,
    DEFAULT_TRANSLATE_SOURCE_LANGUAGE,
    DEFAULT_TRANSLATE_TARGET_LANGUAGE
)

app = FastAPI(
    title="Lexio API",
    version="3.0.0",
    description="Learn languages the way native speakers know them. "
                "Deep linguistic analysis and practical communication "
                "across multiple languages and registers.",
    openapi_tags=[
        {"name": "Dictionary", "description": "Deep linguistic analysis -- single words only"},
        {"name": "Translate", "description": "Practical communication -- words and phrases"},
        {"name": "System", "description": "Health and status"}
    ]
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    schema["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

# ============================================================
# Mount static files for API docs UI
# ============================================================
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# ============================================================
# DICTIONARY ENDPOINT
# ============================================================

@app.post(
    "/dictionary",
    response_model=DictionaryResponse,
    tags=["Dictionary"],
    summary="Deep linguistic analysis of a single word"
)
async def dictionary(
    request: DictionaryRequest,
    x_model_provider: Optional[str] = Header(
        default=None,
        description="Override model provider: 'openai' or 'gemini'"
    ),
    _: str = Depends(verify_api_key)
):
    # Step 1 -- validate and clean the word
    word = validate_single_word(request.word)

    # Step 2 -- determine which provider to use
    provider_name = DEFAULT_MODEL_PROVIDER
    if x_model_provider:
        provider_name = validate_provider(x_model_provider)

    # Step 3 -- get the provider instance
    provider = get_provider(provider_name)

    # Step 4 -- build messages and call the model
    source_language = request.source_language if request.source_language else DEFAULT_DICTIONARY_SOURCE_LANGUAGE
    target_language = request.target_language if request.target_language else DEFAULT_DICTIONARY_TARGET_LANGUAGE
    messages = build_dictionary_messages(word, source_language, target_language)
    result = provider.complete(messages)

    # Step 5 -- handle error response from model
    if result.get("error"):
        raise HTTPException(
            status_code=422,
            detail=result.get("error_message", "Unknown error from model")
        )

    # Step 6 -- build and return the response
    return DictionaryResponse(
        word=word,
        source_language=source_language,
        target_language=target_language,
        definitions=[
            WordDefinition(
                part_of_speech=d["part_of_speech"],
                translation=d["translation"],
                synonyms=d["synonyms"],
                antonyms=d["antonyms"],
                usage=Usage(
                    part_of_speech_notes=d["usage"]["part_of_speech_notes"],
                    forms=d["usage"]["forms"],
                    sentence_examples=[
                        SentenceExample(
                            original=ex["original"],
                            translation=ex["translation"],
                            situation=ex["situation"],
                            tense_or_form=ex.get("tense_or_form")
                        )
                        for ex in d["usage"]["sentence_examples"]
                    ]
                ),
                cultural_context=d["cultural_context"]
            )
            for d in result["definitions"]
        ],
        provider=provider.provider_name
    )


# ============================================================
# TRANSLATE ENDPOINT
# ============================================================

@app.post(
    "/translate",
    response_model=TranslateResponse,
    tags=["Translate"],
    summary="Translate a word or phrase with register variants"
)
async def translate(
    request: TranslateRequest,
    x_model_provider: Optional[str] = Header(
        default=None,
        description="Override model provider: 'openai' or 'gemini'"
    ),
    _: str = Depends(verify_api_key)
):
    # Step 1 -- determine which provider to use
    provider_name = DEFAULT_MODEL_PROVIDER
    if x_model_provider:
        provider_name = validate_provider(x_model_provider)

    # Step 2 -- get the provider instance
    provider = get_provider(provider_name)

    # Step 3 -- resolve language defaults
    source_language = request.source_language \
        if request.source_language else DEFAULT_TRANSLATE_SOURCE_LANGUAGE
    target_language = request.target_language \
        if request.target_language else DEFAULT_TRANSLATE_TARGET_LANGUAGE

    # Step 4 -- build messages and call the model
    messages = build_translate_messages(
        request.input,
        source_language,
        target_language
    )
    result = provider.complete(messages)

    # Step 5 -- handle error response from model
    if result.get("error"):
        raise HTTPException(
            status_code=422,
            detail=result.get("error_message", "Unknown error from model")
        )

    # Step 6 -- build and return the response
    return TranslateResponse(
        input=request.input,
        source_language=source_language,
        target_language=target_language,
        literal_meaning=result.get("literal_meaning"),
        fun_fact=result.get("fun_fact"),
        usage_warning=result.get("usage_warning"),
        variants=[
            TranslateVariant(
                style=v["style"],
                translation=v["translation"],
                notes=v["notes"]
            )
            for v in result["variants"]
        ],
        provider=provider.provider_name
    )


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "version": "3.0.0",
        "default_provider": DEFAULT_MODEL_PROVIDER,
        "default_dictionary_source": DEFAULT_DICTIONARY_SOURCE_LANGUAGE,
        "default_dictionary_target": DEFAULT_DICTIONARY_TARGET_LANGUAGE,
        "default_translate_source": DEFAULT_TRANSLATE_SOURCE_LANGUAGE,
        "default_translate_target": DEFAULT_TRANSLATE_TARGET_LANGUAGE
    }
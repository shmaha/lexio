# ============================================================
# config.py -- All application settings live here
# ============================================================

from dotenv import load_dotenv
import os

load_dotenv()

# --- Supported providers ---
# Used for validation when reading the request header
SUPPORTED_PROVIDERS = ["openai", "gemini"]
# --- Default model provider ---
# This is the fallback when no X-Model-Provider header is sent
# Supported values: "openai" or "gemini"
DEFAULT_MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")

# --- OpenAI settings ---
# Only used when provider is openai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Gemini settings ---
# Only used when provider is gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

# --- Auth ---
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

# --- Input validation ---
MAX_WORD_LENGTH = 50
MIN_WORD_LENGTH = 1

# --- Supported languages ---
# Used for validation in the request body
SUPPORTED_LANGUAGES = [
    "french",
    "german",
    "spanish",
    "italian",
    "portuguese",
    "dutch",
    "polish",
    "russian",
    "arabic",
    "japanese",
    "mandarin",
    "hindi"
]
# --- Default language ---
# This is the fallback when no language is specified in the request body
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "french")
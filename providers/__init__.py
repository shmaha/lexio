# ============================================================
# providers/__init__.py -- Provider factory with singleton pattern
# ============================================================

from providers.base import BaseModelProvider
from providers.openai_provider import OpenAIProvider
from providers.gemini_provider import GeminiProvider
from config import DEFAULT_MODEL_PROVIDER, SUPPORTED_PROVIDERS

# Instantiate providers once at startup -- not per request
_providers = {
    "openai": OpenAIProvider(),
    "gemini": GeminiProvider()
}


def get_provider(provider_name: str = None) -> BaseModelProvider:
    """
    Returns the cached provider instance.
    No new client is created per request.
    """
    name = (provider_name or DEFAULT_MODEL_PROVIDER).lower()

    if name not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider '{name}'. "
            f"Supported: {SUPPORTED_PROVIDERS}"
        )

    return _providers[name]
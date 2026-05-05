# ============================================================
# providers/__init__.py -- Provider factory
# ============================================================
# This is the only place that decides which provider to use.
# The rest of the application calls get_provider() and never
# imports OpenAIProvider or GeminiProvider directly.
# ============================================================

from providers.base import BaseModelProvider
from providers.openai_provider import OpenAIProvider
from providers.gemini_provider import GeminiProvider
from config import DEFAULT_MODEL_PROVIDER, SUPPORTED_PROVIDERS


def get_provider(provider_name: str = None) -> BaseModelProvider:
    """
    Factory function -- returns the correct provider instance.
    
    Args:
        provider_name: "openai" or "gemini". 
                      Falls back to DEFAULT_MODEL_PROVIDER if None.
    
    Returns:
        An instance of the requested provider
    
    Raises:
        ValueError: If provider_name is not in SUPPORTED_PROVIDERS
    """
    name = (provider_name or DEFAULT_MODEL_PROVIDER).lower()

    if name not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider '{name}'. "
            f"Supported: {SUPPORTED_PROVIDERS}"
        )

    if name == "openai":
        return OpenAIProvider()
    elif name == "gemini":
        return GeminiProvider()
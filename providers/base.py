# ============================================================
# providers/base.py -- Abstract base class for all providers
# ============================================================
# Every provider (OpenAI, Gemini, future ones) must implement
# this interface. The rest of the application only ever talks
# to this base class -- never to a provider directly.
#
# This is the core of the provider abstraction pattern.
# Adding a new provider means creating one new file that
# implements this interface. Nothing else changes.
# ============================================================

from abc import ABC, abstractmethod


class BaseModelProvider(ABC):
    
    @abstractmethod
    def complete(self, messages: list[dict]) -> dict:
        """
        Send messages to the model and return parsed JSON response.
        
        Args:
            messages: List of role/content dicts built by build_messages()
        
        Returns:
            Parsed dict matching the TranslationResponse schema
        
        Raises:
            ValueError: If the response cannot be parsed
            RuntimeError: If the provider API call fails
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Returns the name of this provider.
        Used to populate the 'provider' field in the response.
        """
        pass
# ============================================================
# providers/openai_provider.py -- OpenAI implementation
# ============================================================
# Implements BaseModelProvider for the OpenAI API.
# Uses structured outputs to guarantee JSON schema compliance.
# ============================================================

from openai import OpenAI
import json
from providers.base import BaseModelProvider
from config import OPENAI_API_KEY, OPENAI_MODEL


class OpenAIProvider(BaseModelProvider):

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL

    @property
    def provider_name(self) -> str:
        return "openai"

    def complete(self, messages: list[dict]) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3
        )

        raw = response.choices[0].message.content

        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"OpenAI returned invalid JSON: {e}")
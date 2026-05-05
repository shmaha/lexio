# ============================================================
# providers/gemini_provider.py -- Google Gemini implementation
# ============================================================

from google import genai
from google.genai import types
import json
from providers.base import BaseModelProvider
from config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiProvider(BaseModelProvider):

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    @property
    def provider_name(self) -> str:
        return "gemini"

    def complete(self, messages: list[dict]) -> dict:
        system_prompt = ""
        user_message = ""

        for message in messages:
            if message["role"] == "system":
                system_prompt = message["content"]
            elif message["role"] == "user":
                user_message = message["content"]

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                response_mime_type="application/json"
            )
        )

        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Gemini returned invalid JSON: {e}")
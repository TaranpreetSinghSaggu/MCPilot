from backend.app.config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    LLM_PRIMARY,
    OPENAI_API_KEY,
)
from backend.app.llm.gemini import GeminiProvider
from backend.app.llm.groq import GroqProvider
from backend.app.llm.openai import OpenAIProvider


class LLMRouter:

    def __init__(self):
        self.providers = {
            "gemini": GeminiProvider,
            "openai": OpenAIProvider,
            "groq": GroqProvider,
        }

        self.keys = {
            "gemini": GEMINI_API_KEY,
            "openai": OPENAI_API_KEY,
            "groq": GROQ_API_KEY,
        }

    def get_providers(self):
        order = [LLM_PRIMARY]

        for name in ("gemini", "groq", "openai"):
            if name not in order:
                order.append(name)

        return [
            self.providers[name]()
            for name in order
            if self.keys[name]
        ]
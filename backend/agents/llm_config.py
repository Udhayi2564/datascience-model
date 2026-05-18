"""
Shared LLM instance for all agents — Gemini 2.0 Flash via LiteLLM.
"""
import os
from crewai import LLM
from config import get_settings

_settings = get_settings()
os.environ["GEMINI_API_KEY"] = _settings.GEMINI_API_KEY


def get_llm() -> LLM:
    return LLM(
        model="gemini/gemini-2.0-flash",
        api_key=_settings.GEMINI_API_KEY,
        temperature=0.3,
    )

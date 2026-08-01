from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

def get_llm(temperature=0.0):
    """
    Factory para obtener el modelo LLM.
    Prioriza Gemini si existe la API Key, sino hace fallback a Ollama local.
    """
    if settings.gemini_api_key:
        return ChatGoogleGenerativeAI(
            model="gemini-3.5-flash", # Modelo actualizado y rápido para tools
            temperature=temperature,
            api_key=settings.gemini_api_key,
            max_retries=3 # Resiliencia para el límite de la capa gratuita
        )
    else:
        logger.warning("No hay GEMINI_API_KEY. Usando Ollama local como fallback.")
        return ChatOllama(
            model="hermes3", # O el modelo local que esté instalado en Ollama
            temperature=temperature,
        )

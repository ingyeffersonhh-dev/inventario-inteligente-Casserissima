import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# The agent lives at <REPO_ROOT>/agente de ia casserissima/
# This makes all paths resolve automatically regardless of where the repo is copied.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    gemini_api_key: str = ""
    telegram_bot_token: str = ""
    authorized_chat_ids: str = ""
    open_access: bool = False  # Si True, cualquiera con el QR puede hablar con el bot
    
    # Ruta al sistema principal CASSERISISSIMA 2.0 (donde está src/)
    # Por defecto es el directorio padre del agente (el repositorio raiz).
    # Sobrescribir en .env solo si la estructura de carpetas cambia.
    main_system_path: str = str(_REPO_ROOT)
    
    # DB paths (apuntan a la DB del sistema principal)
    db_path: str = f"sqlite+aiosqlite:///{_REPO_ROOT}/src/casserisissima.db"
    db_path_sync: str = f"sqlite:///{_REPO_ROOT}/src/casserisissima.db"

    @property
    def authorized_chats(self) -> List[str]:
        if not self.authorized_chat_ids:
            return []
        return [chat_id.strip() for chat_id in self.authorized_chat_ids.split(',')]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

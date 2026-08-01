import operator
from typing import TypedDict, Annotated, Literal, Sequence, List, Dict, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # El historial de mensajes acumulados en la conversación
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Intención detectada del último mensaje del usuario
    intent: Literal[
        "demand_forecast", 
        "production_planning", 
        "inventory_check", 
        "schedule_job", 
        "general_chat", 
        "unknown",
        ""
    ]
    
    # Herramientas a ejecutar
    tools_to_call: List[Dict[str, Any]]
    
    # Resultados de las herramientas (acumulativo por ciclo)
    tool_results: Annotated[List[Dict[str, Any]], operator.add]
    
    # Datos de contexto de Telegram
    chat_id: str
    
    # Flag para saber si el agente se activó por cron job (True) o por mensaje del usuario (False)
    is_proactive: bool

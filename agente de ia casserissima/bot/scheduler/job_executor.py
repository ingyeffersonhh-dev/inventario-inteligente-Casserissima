import logging
from telegram.ext import Application
from langchain_core.messages import HumanMessage
from agent.graph import graph

logger = logging.getLogger(__name__)

async def execute_proactive_task(app: Application, chat_id: str, job_type: str, parameters: dict):
    """
    Se ejecuta cuando el cron se dispara. Simula un mensaje del usuario.
    """
    logger.info(f"Ejecutando tarea proactiva: {job_type} para {chat_id}")
    
    prompt_map = {
        "demand_forecast": "¿Cuál es el pronóstico de demanda de hoy?",
        "inventory_check": "Revisa el inventario y dame alertas de ROP",
        "production_planning": "¿Cuánto debo producir hoy?"
    }
    
    user_text = prompt_map.get(job_type, "Ejecuta mi tarea programada")
    
    initial_state = {
        "messages": [HumanMessage(content=user_text)],
        "is_proactive": True,
        "chat_id": chat_id,
        "intent": job_type, 
        "tools_to_call": [],
        "tool_results": []
    }
    
    try:
        final_state = await graph.ainvoke(initial_state)
        response_msg = final_state["messages"][-1].content
        
        # Enviar mensaje por Telegram
        await app.bot.send_message(chat_id=chat_id, text=f"🔔 *Alerta Automática:*\n\n{response_msg}")
        
    except Exception as e:
        logger.error(f"Error en tarea proactiva {job_type}: {e}")

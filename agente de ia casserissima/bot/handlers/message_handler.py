import logging
from telegram import Update
from telegram.ext import ContextTypes
from langchain_core.messages import HumanMessage
from agent.graph import graph
from config.settings import settings

logger = logging.getLogger(__name__)

async def is_authorized(update: Update) -> bool:
    if settings.open_access:
        return True  # Acceso abierto: cualquiera con el QR puede hablar
    chat_id = str(update.effective_chat.id)
    if not settings.authorized_chats:
        return True
    return chat_id in settings.authorized_chats

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return

    chat_id = str(update.effective_chat.id)
    user_text = update.message.text
    
    # Indicar que el bot está escribiendo
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    try:
        # Estado inicial para el grafo
        initial_state = {
            "messages": [HumanMessage(content=user_text)],
            "is_proactive": False,
            "chat_id": chat_id,
            "intent": "",
            "tools_to_call": [],
            "tool_results": []
        }
        
        # Ejecutar el grafo de LangGraph
        final_state = await graph.ainvoke(initial_state)
        
        # El resultado final debería estar en el último mensaje
        content = final_state["messages"][-1].content
        
        # A veces el contenido viene serializado como JSON en un string
        if isinstance(content, str) and content.strip().startswith("[") and content.strip().endswith("]"):
            try:
                import json
                parsed_content = json.loads(content)
                if isinstance(parsed_content, list):
                    content = parsed_content
            except Exception:
                pass
                
        if isinstance(content, list):
            response_msg = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
        else:
            response_msg = str(content)
        
        await update.message.reply_text(response_msg)
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        await update.message.reply_text("⚠️ Hubo un problema procesando tu solicitud. Por favor intenta de nuevo.")

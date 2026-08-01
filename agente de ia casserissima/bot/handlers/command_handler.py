from telegram import Update
from telegram.ext import ContextTypes
from config.settings import settings

async def is_authorized(update: Update) -> bool:
    if settings.open_access:
        return True  # Acceso abierto: cualquiera con el QR puede hablar
    chat_id = str(update.effective_chat.id)
    if not settings.authorized_chats:
        return True # Si no hay configurados, permitimos todos (solo dev)
    return chat_id in settings.authorized_chats

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        await update.message.reply_text("No estás autorizado para usar este bot.")
        return
        
    welcome_msg = (
        "🍰 *CASSERISSIMA 2.0 — Agente IA de Operaciones*\n\n"
        "Sistema de apoyo a decisiones para pastelería artesanal.\n"
        "Tesis: Br. Jorfran Gil y Br. Yefferson Hernández — Universidad de Oriente.\n\n"
        "_Puedo ayudarte con:_\n"
        "📊 *Predicción de demanda* — pronóstico por producto (Random Forest)\n"
        "🧑‍🍳 *Producción óptima* — cuánto hornear hoy (modelo Newsvendor)\n"
        "📦 *Inventario* — stock e insumos en punto de reorden (ROP)\n"
        "⏰ *Alertas* — recordatorios diarios automatizados\n\n"
        "Escríbeme en lenguaje natural. Ej: _\"¿cuánto de torta 3 leches debo producir mañana?\"_"
    )
    await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    await update.message.reply_text("Escríbeme como si hablaras con tu asistente. Ej: '¿Cuánto de 3 leches debo producir mañana?'")

async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    await update.message.reply_text("Funcionalidad de trabajos programados en desarrollo 🚧")

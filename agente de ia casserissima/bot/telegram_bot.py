from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.settings import settings
import logging
from bot.handlers.command_handler import start_command, help_command, jobs_command
from bot.handlers.message_handler import handle_text_message

logger = logging.getLogger(__name__)

def create_bot_app() -> Application:
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN no configurado. El bot no podrá iniciar.")
        return None
        
    app = Application.builder().token(settings.telegram_bot_token).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("jobs", jobs_command))
    
    # Mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    return app

import asyncio
import logging
import multiprocessing
from config.settings import settings
from bot.telegram_bot import create_bot_app
from bot.scheduler.persistent_scheduler import start_scheduler, scheduler
from database.connection import AsyncSessionLocal
from database.models import ScheduledJob
from sqlalchemy import select
from apscheduler.triggers.cron import CronTrigger
from bot.scheduler.job_executor import execute_proactive_task

from mcp_server.server import mcp

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

global_app = None

def get_telegram_app():
    return global_app

async def restore_scheduled_jobs(app):
    """Lee ScheduledJobs de SQLite y los re-registra en APScheduler."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ScheduledJob).where(ScheduledJob.is_active == True))
        jobs = result.scalars().all()
        
        for job in jobs:
            import json
            params = json.loads(job.parameters)
            scheduler.add_job(
                execute_proactive_task,
                CronTrigger.from_crontab(job.cron_expression),
                id=f"job_{job.id}",
                kwargs={
                    "app": app,
                    "chat_id": job.chat_id,
                    "job_type": job.job_type,
                    "parameters": params,
                },
                replace_existing=True,
            )
        logger.info(f"Se restauraron {len(jobs)} trabajos programados de la DB.")

def run_mcp_server():
    """Ejecuta el servidor FastMCP en un proceso separado."""
    logger.info("Iniciando MCP Server (SSE) en puerto 8001...")
    mcp.run(transport="sse", port=8001)

async def notify_startup(app):
    """Envía un mensaje de saludo inicial a todos los chat IDs autorizados."""
    if settings.authorized_chats:
        for chat_id in settings.authorized_chats:
            try:
                await app.bot.send_message(
                    chat_id=chat_id,
                    text="🤖 *CASSERISISSIMA 2.0 Agent Ecosystem* está *en línea* y listo para operar. 🍰📊\n\n¿En qué te puedo asistir hoy, Gerente?",
                    parse_mode="Markdown"
                )
                logger.info(f"Mensaje de inicio enviado a {chat_id}")
            except Exception as e:
                logger.error(f"No se pudo enviar mensaje de inicio a {chat_id}: {e}")

async def main():
    global global_app
    logger.info("Iniciando CASSERISISSIMA 2.0 Agent Ecosystem...")
    
    # 1. Iniciar MCP Server en proceso aparte (evitar bloqueos de event loop)
    mcp_process = multiprocessing.Process(target=run_mcp_server)
    mcp_process.start()
    
    # 2. Iniciar Bot de Telegram
    app = create_bot_app()
    if not app:
        logger.error("Saliendo porque no hay Token de Telegram.")
        mcp_process.terminate()
        return
        
    global_app = app
    await app.initialize()
    await app.start()
    
    # 3. Iniciar scheduler y restaurar jobs persistentes
    start_scheduler()
    await restore_scheduled_jobs(app)
    
    # 4. Enviar notificación de inicio
    await notify_startup(app)
    
    # 5. Iniciar polling
    logger.info("Bot de Telegram iniciado y listo para recibir mensajes. Presiona Ctrl+C para detener.")
    try:
        await app.updater.start_polling()
        # Mantener el event loop vivo
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Apagando sistema...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        mcp_process.terminate()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    asyncio.run(main())

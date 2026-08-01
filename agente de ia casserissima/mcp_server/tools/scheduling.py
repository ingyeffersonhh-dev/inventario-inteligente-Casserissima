import json
from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import ScheduledJob
from bot.scheduler.persistent_scheduler import scheduler
from apscheduler.triggers.cron import CronTrigger

async def create_scheduled_job(chat_id: str, job_type: str, cron_expression: str, description: str, parameters: dict = None) -> dict:
    """Registra una nueva tarea programada persistente para el gerente."""
    # Nota: el parámetro chat_id usualmente viene del contexto del usuario,
    # pero aquí lo pedimos como argumento para flexibilidad.
    async with AsyncSessionLocal() as session:
        job = ScheduledJob(
            chat_id=chat_id,
            job_type=job_type,
            cron_expression=cron_expression,
            description=description,
            parameters=json.dumps(parameters or {})
        )
        session.add(job)
        await session.flush()
        
        # Importación diferida para evitar ciclos
        from main import get_telegram_app
        from bot.scheduler.job_executor import execute_proactive_task
        
        app = get_telegram_app()
        if app:
            # Agregamos al scheduler en memoria/BD (apscheduler)
            scheduler.add_job(
                execute_proactive_task,
                CronTrigger.from_crontab(cron_expression),
                id=f"job_{job.id}",
                kwargs={
                    "app": app,
                    "chat_id": chat_id,
                    "job_type": job_type,
                    "parameters": parameters or {}
                },
                replace_existing=True
            )
            
        await session.commit()
        return {"status": "success", "message": f"Tarea '{description}' registrada con cron '{cron_expression}'."}

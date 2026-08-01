import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from config.settings import settings
from database.models import Base

async def init_db():
    engine = create_async_engine(settings.db_path, echo=True)
    async with engine.begin() as conn:
        # Crea las tablas faltantes sin borrar las existentes
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Migración completada. Nuevas tablas creadas en la BD existente.")

if __name__ == "__main__":
    asyncio.run(init_db())

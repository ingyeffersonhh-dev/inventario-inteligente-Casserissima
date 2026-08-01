"""
CASSERISSIMA 2.0 — FastAPI Backend
Punto de entrada principal. Inicializa DB, seed y routers.
"""
import logging
import os
import sys

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Agregar el directorio backend al path para imports relativos
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

# Configurar logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Startup: inicializar DB y seed usando Lifespan ───────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la base de datos y ejecuta el seed de datos al arrancar."""
    from db.database import init_db, SessionLocal
    from db.seed import run_seed

    logger.info("═" * 60)
    logger.info("  CASSERISSIMA 2.0 — Motor Predictivo arrancando...")
    logger.info("═" * 60)

    # Crear tablas
    init_db()
    logger.info("✓ Base de datos SQLite inicializada.")

    # Ejecutar seed
    db = SessionLocal()
    try:
        stats = run_seed(db)
        logger.info(
            f"✓ Seed completado: "
            f"productos={stats['products']}, "
            f"ventas_s1={stats['sales_s1']}, "
            f"ventas_s2={stats['sales_s2']}, "
            f"ventas_s3={stats['sales_s3']}, "
            f"ingredientes={stats['ingredients']}"
        )
    except Exception as e:
        logger.error(f"Error ejecutando seed: {e}")
    finally:
        db.close()

    logger.info("✓ API lista en http://localhost:8000/docs")
    logger.info("═" * 60)
    
    yield  # La aplicación se ejecuta aquí
    
    logger.info("Apagando Motor Predictivo CASSERISSIMA 2.0...")


# ── Aplicación FastAPI ────────────────────────────────────────────────────────

app = FastAPI(
    title="CASSERISSIMA 2.0 — Motor Predictivo",
    description="Sistema de pronóstico de demanda y gestión de inventario para pastelería venezolana.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allow_origins = [frontend_url, "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Manejador Global de Excepciones ───────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado en {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno en el servidor.", "error_type": type(exc).__name__},
    )

# ── Routers ───────────────────────────────────────────────────────────────────
from routers import scenarios, dashboard, sales, inventory, predictions, insights  # noqa

PREFIX = "/api/v1"
app.include_router(scenarios.router,   prefix=PREFIX, tags=["Escenarios"])
app.include_router(dashboard.router,   prefix=PREFIX, tags=["Dashboard"])
app.include_router(sales.router,       prefix=PREFIX, tags=["Ventas"])
app.include_router(inventory.router,   prefix=PREFIX, tags=["Inventario"])
app.include_router(predictions.router, prefix=PREFIX, tags=["Predicciones"])
app.include_router(insights.router,    prefix=PREFIX, tags=["Insights IA"])


# Lifespan define el inicio y apagado, el código del seed está arriba.


@app.get("/health", tags=["Sistema"])
async def health_check():
    return {
        "status":  "ok",
        "service": "CASSERISSIMA 2.0 Predictive Engine",
        "version": "2.0.0",
    }

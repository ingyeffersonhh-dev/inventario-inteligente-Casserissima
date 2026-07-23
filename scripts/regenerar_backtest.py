"""
CASSERISISSIMA 2.0 — Wrapper para regenerar el reporte OE4 de backtesting.
Punto de entrada determinista para la tesis.

Uso:
    python scripts/regenerar_backtest.py            # full: escenario 2, todos los productos
    python scripts/regenerar_backtest.py --smoke    # smoke rápido (1 producto)
    python scripts/regenerar_backtest.py --scenario 3 --max-products 5

Imprime JSON + escribe CSVs a results/.
"""
import os
import sys

# Asegurar que src/ esté en el path (el módulo principal está ahí)
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SRC_DIR = os.path.join(REPO_ROOT, "src")
sys.path.insert(0, SRC_DIR)

# database.py resuelve DATABASE_URL como ruta relativa (./casserisissima.db)
# y load_dotenv() busca .env en el CWD. Desde la raíz del repo eso apuntaría a
# una BD vacía. Fijamos la ruta absoluta a la BD sembrada en src/ ANTES de
# importar (load_dotenv con override=False respetará este valor).
os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(SRC_DIR, "casserisissima.db"),
)

if __name__ == "__main__":
    # Reenviar al CLI del módulo core.ml.backtest_report, forzando --json --csv
    # para que la regeneración siempre emita resultados serializables.
    from core.ml.backtest_report import main

    # Inyectar --json --csv si no están ya presentes (regeneración determinista)
    argv = list(sys.argv[1:])
    if "--json" not in argv:
        argv.append("--json")
    if "--csv" not in argv:
        argv.append("--csv")
    sys.argv = [sys.argv[0]] + argv
    main()

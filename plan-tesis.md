# Plan de Trabajo — Tesis: Sistema Predictivo ML para Inventarios Perecederos

**Autores:** Br. Jorfran Gil, Br. Yefferson Hernández  
**Universidad de Oriente, Núcleo de Monagas**  
**Repo:** `CASSERISISSIMA 2.0` (FastAPI + Next.js + ML)

---

## Leyenda

| Símbolo | Significado |
|---------|-------------|
| ✅ | Completado |
 | 📝 | Texto (se pasa por chat, se pega en Word) |
| 📊 | Figura / Diagrama / Gráfico |
| 💻 | Código (cambios en el repo) |

---

## Bloque 1 — ✅ Ya completado

| Paso | Qué | Dónde | Estado |
|------|-----|-------|--------|
| A.1 | Objetivos Específicos reformulados | §1.2.2 (párrafos 54-57) + Cuadro 1 | ✅ |
| A.2 | Cap III actualizado (pandas, TimeSeriesSplit, RandomizedSearchCV, MAE, FastAPI+Next.js) | §3.4, §3.5, §3.6 | ✅ |
| A.3 | Cuadro Operativo alineado con sistema real | Cuadro 1 | ✅ |

---

## Bloque 2 — 📝 Documento (Pasos 1-23)

### B.1 — Estructura Metodológica

| # | Qué | Tipo | Prioridad |
|---|-----|------|-----------|
| 1 | Matriz de Consistencia | 📝 Tabla | 🔴 Alta |
| 2 | Operacionalización de Variables | 📝 Tabla | 🔴 Alta |
| 3 | Cronograma / Diagrama Gantt | 📊 Python | 🟡 Media |

### B.2 — Fase I: Diagnóstico

| # | Qué | Tipo | Prioridad |
|---|-----|------|-----------|
| 4 | Diagrama flujo inventario actual | 📊 Excalidraw | 🟡 Media |
| 5 | Gráfico clasificación ABC (Pareto) | 📊 Python | 🟡 Media |
| 6 | Gráfico patrones de demanda | 📊 Python | 🟡 Media |
| 7 | Redactar §3.7.1 con hallazgos | 📝 Texto | 🔴 Alta |

### B.3 — Fase II: Modelado

| # | Qué | Tipo | Prioridad |
|---|-----|------|-----------|
| 8 | Diagrama pipeline ML (entrenamiento + evaluación) | 📊 Excalidraw | 🔴 Alta |
| 9 | Feature importance (Random Forest) | 📊 Python | 🟡 Media |
| 10 | Predicción vs demanda real (gráfico) | 📊 Python | 🟡 Media |
| 11 | Redactar §3.7.2 con resultados | 📝 Texto | 🔴 Alta |

### B.4 — Fase III: Desarrollo (lo que marcó el tutor)

| # | Qué | Tipo | Prioridad |
|---|-----|------|-----------|
| 12 | Arquitectura del sistema (FastAPI + Next.js) | 📊 Excalidraw | 🔴 Alta |
| 13 | Concepto ROP Evolutivo con OR-Tools | 📊 Excalidraw | 🔴 Alta |
| 14 | Screenshot del dashboard real | 📸 Captura manual | 🟡 Media |
| 15 | Redactar §3.7.3 con resultados | 📝 Texto | 🔴 Alta |

### B.5 — Fase IV: Validación

| # | Qué | Tipo | Prioridad |
|---|-----|------|-----------|
| 16 | Diagrama walk-forward / backtesting | 📊 Excalidraw | 🔴 Alta |
| 17 | Mermas: baseline vs sistema (gráfico) | 📊 Python | 🔴 Alta |
| 18 | Evolución de métricas por ventana temporal | 📊 Python | 🟡 Media |
| 19 | Redactar §3.7.4 con resultados | 📝 Texto | 🔴 Alta |

### B.6 — Secciones Complementarias

| # | Qué | Tipo | Prioridad |
|---|-----|------|-----------|
| 20 | Validez y Confiabilidad de instrumentos | 📝 Texto (§3.5) | 🟡 Media |
| 21 | Limitaciones y Amenazas a la Validez | 📝 Texto (§3.8 nueva) | 🟡 Media |
| 22 | Declarar datos sintéticos calibrados con juicio experto | 📝 Texto | 🟡 Media |
| 23 | Declarar RF + LightGBM como generalización de modelos | 📝 Texto | 🟡 Media |

---

## Bloque 3 — 💻 Código (Pasos 24-27)

> Se hace DESPUÉS de que el documento esté completamente redactado.

| # | OE | Qué | Prioridad |
|---|----|-----|-----------|
| 24 | OE4 | Backtesting walk-forward + simulación de mermas + baseline comparativo | 🔴 Alta |
| 25 | OE3 | Entidad `reorder_points` en DB + endpoint + dashboard + lead times | 🟡 Media |
| 26 | OE1 | Notebook de diagnóstico + requerimientos de información formalizados | 🟡 Media |
| 27 | — | Capítulo IV: agente LangGraph como recomendación | 🟢 Baja |

---

## Orden de Ejecución Sugerido

```
 1 →  2 →  3 (Matriz → Operacionalización → Gantt)
 4 →  5 →  6 →  7 (Fase I completa)
 8 →  9 → 10 → 11 (Fase II completa)
12 → 13 → 14 → 15 (Fase III completa)
16 → 17 → 18 → 19 (Fase IV completa)
20 → 21 → 22 → 23 (Complementarias)
                ↓
          [Redacción lista]
                ↓
24 → 25 → 26 → 27 (Código)
```

---

## Notas Clave

- **Preferencia de trabajo:** el texto se pasa por chat para que el autor copie/pegue en Word. No se edita el `.docx` directamente.
- **Datos sintéticos:** `seed.py` genera datos calibrados con juicio experto del personal operativo, no al azar.
- **Agente LangGraph:** queda fuera del Capítulo III. Va en Capítulo IV como recomendación.
- **Skills disponibles para figuras:** `excalidraw-diagram-generator`, `pandas-pro`, `python-executor`, `machine-learning`.

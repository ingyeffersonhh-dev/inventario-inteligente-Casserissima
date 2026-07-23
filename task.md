# Progreso — Plan de Tesis Casserisissima 2.0

**Autores:** Br. Jorfran Gil — Br. Yefferson Hernández  
**UDO Monagas | agosto 2026**

---

## Bloque 1 — ✅ Completado

| Paso | Qué | Estado |
|------|-----|--------|
| A.1 | Objetivos Específicos reformulados | ✅ |
| A.2 | Cap III actualizado (pandas, TimeSeriesSplit, RandomizedSearchCV, MAE, FastAPI+Next.js) | ✅ |
| A.3 | Cuadro Operativo alineado con sistema real | ✅ |

---

## Bloque 2 — Documento (Pasos 1-23)

### B.1 — Estructura Metodológica

| # | Qué | Tipo | Estado |
|---|-----|------|--------|
| 1 | Matriz de Consistencia | 📝 Tabla | ✅ Generado en `docs/B1_estructura_metodologica.md` |
| 2 | Operacionalización de Variables | 📝 Tabla | ✅ Generado en `docs/B1_estructura_metodologica.md` |
| 3 | Cronograma / Diagrama Gantt | 📊 Python | ✅ Imagen en `docs/images/gantt_cronograma.png` (migrado a paleta azul-gris coherente) |

### B.2 — Fase I: Diagnóstico

| # | Qué | Tipo | Estado |
|---|-----|------|--------|
| 4 | Diagrama flujo inventario actual | 📊 Python | ✅ Imagen en `docs/images/diagrama_flujo_inventario.png` |
| 5 | Gráfico clasificación ABC (Pareto) | 📊 Python | ✅ Imagen en `docs/images/clasificacion_abc.png` (ajustado para evitar solapamientos) |
| 6 | Gráfico patrones de demanda | 📊 Python | ✅ Imagen en `docs/images/patrones_demanda.png` (ajustado para evitar solapamientos) |
| 7 | Redactar §3.7.1 con hallazgos | 📝 Texto | ✅ `docs/B2_fase1_diagnostico.md` + `docs/fase1_para_word.html` |

### B.3 — Fase II: Modelado Predictivo y Cuantificación de Riesgo

| # | Qué | Tipo | Estado |
|---|-----|------|--------|
| 8 | Diagrama pipeline ML (RF vs LightGBM) | 📊 Excalidraw | ✅ Generado en `docs/images/pipeline_ml.excalidraw` |
| 9 | Gráficas de Error (MAE, RMSE, MAPE) por Producto | 📊 Python | ✅ Imágenes en `docs/images/fig01_mae_por_producto.png`, `fig02_metricas_comparadas.png` y `fig03_modelos_ganadores.png` |
| 10 | Simulación Monte Carlo (Probabilidad Quiebre Stock) | 📊 Python | ✅ Imagen en `docs/images/simulacion_montecarlo.png` |
| 11 | Comparativa y Backtesting (SARIMA vs ML) | 📝 Texto | ✅ Redactado en `docs/B3_fase2_predictiva.md` y `docs/fase2_para_word.html` |
| 12 | Redactar §3.7.2 con resultados del Modelado | 📝 Texto | ✅ Redactado en `docs/B3_fase2_predictiva.md` + `docs/fase2_para_word.html` |

### B.4 — Fase III: Diseño de Solución Smart Supply Chain (TO-BE)

| # | Qué | Tipo | Estado |
|---|-----|------|--------|
| 13 | Arquitectura Blockchain, Smart Contracts e IIoT | 📊 Excalidraw | ⬜ Pendiente |
| 14 | Cálculo de Punto de Reorden Evolutivo y Newsvendor | 📊 Python | ⬜ Pendiente |
| 15 | Protocolos de Inspección IA (PR-CAL) e ISO 27001 | 📝 Texto | ⬜ Pendiente |
| 16 | Redactar §3.7.3 con la propuesta tecnológica | 📝 Texto | ⬜ Pendiente |

### B.5 — Fase IV: Simulación Operativa y Factibilidad

| # | Qué | Tipo | Estado |
|---|-----|------|--------|
| 17 | Simulación FlexSim (Escenario AS-IS vs TO-BE) | 📊 Diagrama | ⬜ Pendiente |
| 18 | Ergonomía con IA (YOLOv8) y Therbligs 4.0 | 📊 Imagen | ⬜ Pendiente |
| 19 | Red CPM/PERT Probabilística y Curvas de Aprendizaje | 📊 Tabla/Gráfico | ⬜ Pendiente |
| 20 | Redactar §3.7.4 con la validación de factibilidad | 📝 Texto | ⬜ Pendiente |

### B.6 — Secciones Complementarias

| # | Qué | Tipo | Estado |
|---|-----|------|--------|
| 20 | Validez y Confiabilidad de instrumentos | 📝 Texto (§3.5) | ⬜ Pendiente |
| 21 | Limitaciones y Amenazas a la Validez | 📝 Texto (§3.8 nueva) | ⬜ Pendiente |
| 22 | Declarar datos sintéticos calibrados con juicio experto | 📝 Texto | ⬜ Pendiente |
| 23 | Declarar RF + LightGBM como generalización de modelos | 📝 Texto | ⬜ Pendiente |

---

## Bloque 3 — Código (Pasos 24-27)

> Se hace DESPUÉS de que el documento esté completamente redactado.

| # | OE | Qué | Estado |
|---|----|-----|--------|
| 24 | OE4 | Backtesting walk-forward + simulación de mermas + baseline comparativo | ⬜ Pendiente |
| 25 | OE3 | Entidad `reorder_points` en DB + endpoint + dashboard + lead times | ⬜ Pendiente |
| 26 | OE1 | Notebook de diagnóstico + requerimientos de información formalizados | ⬜ Pendiente |
| 27 | — | Capítulo IV: agente LangGraph como recomendación | ⬜ Pendiente |

---

## Siguiente paso sugerido: Paso 13

**B.4.1 — Arquitectura Blockchain, Smart Contracts e IIoT** (Excalidraw / SVG)  
Representa el diseño tecnológico del flujo de información seguro, la validación de materias primas mediante Smart Contracts en la red Blockchain e integración con sensores de temperatura/humedad IIoT.

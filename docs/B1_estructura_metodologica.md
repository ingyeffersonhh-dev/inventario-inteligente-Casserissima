# Bloque B.1 — Estructura Metodológica (Versión Resumida)
## Sistema Predictivo Basado en Machine Learning para la Optimización de Inventarios Perecederos en la Pastelería Casserissima C.A.

---

## Paso 1 — Matriz de Consistencia (Resumida)

Esta versión agrupa la información por objetivo para facilitar su lectura en una sola página de Word, manteniendo el rigor de las relaciones metodológicas.

**Cuadro X. Matriz de Consistencia**

| **Objetivos** | **Variables** | **Indicadores Clave** | **Metodología** |
|---|---|---|---|
| **General:** Proponer un sistema predictivo basado en ML para la optimización de inventarios perecederos en la Pastelería Casserissima. | **VI:** Sistema predictivo ML <br><br> **VD:** Optimización de inventarios | Reducción de mermas (%), Nivel de servicio, Precisión (MAPE, RMSE) | **Tipo:** Proyectiva, documental <br> **Diseño:** Transversal, backtesting <br> **Población/Muestra:** Histórico de ventas (90 días) y personal clave (n=3) |
| **OE1 (Diagnóstico):** Diagnosticar el estado actual de los flujos de inventario y la demanda. | **VD:** Flujo actual de inventario | Clasificación ABC, rotación, mermas actuales (12%), ventas perdidas (15%) | **Técnica:** Entrevista, revisión documental <br> **Instrumento:** Guía de entrevista |
| **OE2 (Modelado):** Determinar la precisión del modelo Random Forest. | **VI:** Precisión del modelo predictivo | Error porcentual (MAPE < 15%), RMSE, MAE | **Técnica:** Análisis computacional <br> **Instrumento:** Scripts ML (Python) |
| **OE3 (Desarrollo):** Estructurar el sistema (ROP Evolutivo + Dashboard). | **VI:** Diseño de la arquitectura del sistema | Cobertura funcional del ROP calculado e integración del dashboard | **Técnica:** Desarrollo tecnológico <br> **Instrumento:** FastAPI + Next.js |
| **OE4 (Validación):** Validar la reducción de mermas y optimización de stock. | **VD:** Desempeño predictivo del sistema | Comparación de mermas (baseline vs sistema), Δ nivel de servicio | **Técnica:** Walk-forward validation <br> **Instrumento:** Script de Backtesting |

*Fuente: Elaboración propia (2026).*

---

## Paso 2 — Operacionalización de Variables (Resumida)

Se han omitido las definiciones teóricas extensas (ya que van en el texto del marco teórico) para enfocarnos directamente en las dimensiones, indicadores y cómo se van a medir.

**Cuadro X+1. Operacionalización de Variables**

| **Variable** | **Dimensiones** | **Indicadores** | **Técnica / Instrumento** |
|---|---|---|---|
| **VI: Sistema predictivo basado en Machine Learning** <br><br> *(Integración de Random Forest, cálculo dinámico de reposición y tablero gerencial).* | **1. Algoritmo Predictivo** | • MAPE, RMSE y MAE del modelo <br> • Hiperparámetros (*n_estimators*, *max_depth*) | Entrenamiento en Python (scikit-learn). TimeSeriesSplit. |
| | **2. Lógica de Reposición** | • Valor del Punto de Reorden (ROP) <br> • Stock de seguridad calculado | Módulo matemático en backend (FastAPI). |
| | **3. Interfaz Gerencial** | • Módulos funcionales del Dashboard <br> • Tiempos de respuesta (API) | Pruebas de software sobre el frontend (Next.js). |
| **VD: Optimización de inventarios perecederos** <br><br> *(Equilibrio entre minimizar mermas por caducidad y evitar rupturas de stock).* | **1. Control de Existencias** | • Clasificación ABC de insumos <br> • Rotación de inventario (veces/mes) | Revisión de históricos de almacén. |
| | **2. Minimización de Mermas** | • % de merma actual (Línea base: 12%) <br> • Reducción lograda post-simulación | Script de simulación y Backtesting comparativo. |
| | **3. Eficiencia en Reposición** | • % de ventas perdidas (Línea base: 15%) <br> • Lead time de reposición real | Backtesting (Walk-forward validation). |

*Fuente: Elaboración propia (2026).*

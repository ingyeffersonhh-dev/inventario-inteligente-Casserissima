# ANÁLISIS COMPLETO: IMÁGENES Y ANÁLISIS COSTO-BENEFICIO
## Tesis: Sistema Predictivo basado en ML para Optimización de Inventarios Perecederos
## Pastelería Casseríssima C.A.

---

## PARTE 1: DIAGNÓSTICO DE IMÁGENES

### Mapeo Figura → Imagen → Dimensiones

| # Figura | Descripción | Imagen | Dimensiones | Tamaño | Estado |
|-----------|-------------|--------|-------------|--------|--------|
| Fig 1 | Organigrama de la empresa | image2.png | **358×338 px** | **12.1 KB** | ⚠️ CRÍTICO |
| Fig 2 | Prototipo interfaz tablero control | image3.png | 1918×866 px | 90.2 KB | ✅ OK |
| Fig 3 | Arquitectura Random Forest | image4.png | 850×562 px | 128.5 KB | ⚠️ REGULAR |
| Fig 4 | Demanda real vs pronóstico (MAPE/RMSE) | image5.png | 1221×628 px | 204.5 KB | ✅ OK |
| Fig 5 | Curva distribución Newsvendor | image6.png | 990×590 px | 92.5 KB | ⚠️ REGULAR |
| Fig 6 | Cronograma Gantt | image7.png | 1405×719 px | 65.7 KB | ✅ OK |
| Fig 7 | Diagrama flujo inventario actual | image8.png | 1661×949 px | 138.2 KB | ✅ OK |
| Fig 8 | Patrón demanda diaria Tres Leches | image9.png | 1459×729 px | 147.6 KB | ✅ OK |
| Fig 9 | Clasificación ABC Pareto | image10.png | 1483×865 px | 126.6 KB | ✅ OK |
| Fig 10 | Arquitectura pipeline ML | image11.png | 1793×646 px | 208.4 KB | ✅ OK |
| Fig 11 | MAE por producto | image12.png | 1623×808 px | 73.4 KB | ✅ OK |
| Fig 12 | Métricas error por SKU | image13.png | 1652×535 px | 81.1 KB | ✅ OK |
| Fig 13 | Distribución probabilidad DDLT Monte Carlo | image14.png | 1500×902 px | 136.4 KB | ✅ OK |
| Fig 14 | Arquitectura Lógica | image15.png | 1124×1225 px | 157.6 KB | ✅ OK |
| Fig 15 | Diagrama Entidad-Relación | image16.png | 1429×941 px | 177.4 KB | ✅ OK |
| Fig 16 | Flujo ROP Evolutivo | image17.png | 1352×1161 px | 142.8 KB | ✅ OK |
| Fig 17 | Captura Tablero de Control | image18.png | 1920×1080 px | 248.6 KB | ✅ OK |
| Fig 18 | Reducción de Mermas | image19.png | 1418×945 px | 89.9 KB | ✅ OK |
| Fig 19 | Reducción Quiebres Stock | image20.png | 1264×843 px | 64.5 KB | ✅ OK |
| Fig 20 | Evolución Inventario vs Demanda | image21.png | 1486×691 px | 170.1 KB | ✅ OK |

### Imágenes con problemas detectados

#### PROBLEMA 1: Figura 1 — Organigrama (CRÍTICO)
- **Imagen**: image2.png
- **Dimensiones**: 358×338 píxeles
- **Tamaño**: 12.1 KB
- **Diagnóstico**: Esta imagen es extremadamente pequeña. En una página A4 a 100% de escala, una imagen de 358 px de ancho se verá borrosa, pixelada y con texto ilegible. Es la causa principal del reclamo del tutor.
- **Causa probable**: Se insertó una imagen descargada de internet con resolución baja, o se exportó desde una herramienta con configuración de calidad mínima.

#### PROBLEMA 2: Figura 3 — Arquitectura Random Forest (MODERADO)
- **Imagen**: image4.png
- **Dimensiones**: 850×562 píxeles
- **Tamaño**: 128.5 KB
- **Diagnóstico**: Aceptable pero al límite. En impresión a página completa puede perder nitidez en los textos internos del diagrama.

#### PROBLEMA 3: Figura 5 — Curva Newsvendor (MODERADO)
- **Imagen**: image6.png
- **Dimensiones**: 990×590 píxeles
- **Tamaño**: 92.5 KB
- **Diagnóstico**: Marginal. Los textos pequeños de los ejes pueden resultar difíciles de leer.

#### PROBLEMA 4: Logo/Imagen duplicada
- **image1.png** (173×173 px, 44.3 KB) aparece en el encabezado (posiblemente logo de la universidad) Y también se referencia como Figura 20 en el índice. Verificar que la Figura 20 use correctamente image21.png.

---

## PARTE 2: PLAN DE ACCIÓN PARA MEJORAR LAS IMÁGENES

### OPCIÓN A: Regenerar las imágenes problemáticas (RECOMENDADA)

**Para Figura 1 — Organigrama (Prioridad ALTA):**
1. Si el organigrama fue creado en Visio, PowerPoint, Canva o similar → abrir el archivo fuente y re-exportar a PNG con resolución mínima de 300 DPI o al menos 1500×1500 px
2. Si no se tiene el archivo fuente → reconstruir el organigrama usando:
   - **draw.io** (gratis, exporta PNG a alta resolución)
   - **Canva** (plantillas de organigramas)
   - **PowerPoint** → exportar como imagen PNG a 300 DPI
3. Si el organigrama viene del documento original de la empresa → solicitar la fuente o fotografiarlo con buena iluminación y recortar

**Para Figura 3 — Arquitectura Random Forest (Prioridad MEDIA):**
1. Regenerar desde la herramienta original (probablemente draw.io, Lucidchart o similar)
2. Exportar con al menos 2000 px de ancho
3. Alternativa: recrear en PowerPoint con formas y exportar como PNG de alta calidad

**Para Figura 5 — Curva Newsvendor (Prioridad MEDIA):**
1. Regenerar desde matplotlib/Python con `dpi=300` en `savefig()`
2. Código de ejemplo:
   ```python
   import matplotlib.pyplot as plt
   import numpy as np
   # ... código del gráfico ...
   plt.savefig('figura5_newsvendor.png', dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
   ```

### OPCIÓN B: Mejorar calidad de inserción en Word

Si no se puede regenerar las imágenes originales:
1. En Word, hacer clic derecho sobre la imagen → "Formato de imagen"
2. Pestaña "Tamaño y propiedades" → verificar que no esté comprimida
3. Desmarcar "Comprimir imágenes" en Archivo → Opciones → Avanzadas
4. Para la Figura 1 específicamente: reducir el tamaño de la imagen en la página para que se vea nítida a menor escala, y agregar una nota al pie con más detalle

### OPCIÓN C: Estándares de calidad para todas las imágenes (REGLA GENERAL)

Para todas las 20 figuras, asegurar:
- **Resolución mínima**: 1200 px de ancho (ideal: 1800+ px)
- **Formato**: PNG (ya están en PNG, correcto)
- **Compresión**: Desactivar compresión de imágenes en Word
- **DPI al insertar**: Al menos 150 DPI en la impresión final
- **Texto legible**: Todo texto dentro de las imágenes debe ser legible al imprimir a tamaño completo

### OPCIÓN D: Herramientas gratuitas para regenerar gráficos

| Gráfico | Herramienta sugerida | Ventaja |
|---------|---------------------|---------|
| Fig 1 (Organigrama) | draw.io / Lucidchart | Vectorial, exporta HD |
| Fig 3 (Arquitectura ML) | draw.io | Diagramas técnicos |
| Fig 5 (Newsvendor) | Python matplotlib | Ya tienes los datos |
| Fig 6 (Gantt) | draw.io / ProjectLibre | Escalable |
| Fig 7 (Flujo) | draw.io | Diagramas de flujo |
| Fig 14 (Arquitectura) | draw.io | Ya está bien |
| Fig 15 (Entidad-Relación) | draw.io / dbdiagram.io | Ya está bien |
| Fig 16 (Flujo ROP) | draw.io | Ya está bien |

---

## PARTE 3: ANÁLISIS COSTO-BENEFICIO DE LA PROPUESTA

### 3.1 Línea Base Diagnóstica (Situación Actual)

Según el diagnóstico de la tesis, la Pastelería Casseríssima presenta las siguientes ineficiencias:

| Indicador | Valor Actual (Línea Base) |
|-----------|--------------------------|
| Merma mensual por caducidad de insumos | 12% |
| Pérdidas por sobreproducción de bienes finales | 8% |
| Ventas perdidas por rupturas de stock | 15% |
| Retraso logístico de proveedores (Lead time) | 48 a 72 horas |
| Toma de decisiones | Empírica y visual |
| Catálogo de insumos | ~80 SKU |
| Personal del área | 3 empleados |

### 3.2 Costos Estimados de la Situación Actual (Escenario Sin Sistema)

Para cuantificar el impacto financiero, se estima el costo de las ineficiencias actuales:

**Supuestos de estimación:**
- Ventas mensuales estimadas de la pastelería (sector repostería PYME en Maturín): $800 - $1,500 USD/mes
- Se utiliza un valor conservador de $1,000 USD/mes como base de cálculo
- Los costos de insumos representan aproximadamente el 40-50% de las ventas

**Cálculo de pérdidas mensuales:**

| Concepto | Cálculo | Pérdida Mensual Estimada |
|----------|---------|--------------------------|
| **Merma por caducidad (12%)** | 12% × $500 (costo insumos) | $60.00 USD |
| **Sobreproducción (8%)** | 8% × $1,000 (ventas) | $80.00 USD |
| **Ventas perdidas por quiebre de stock (15%)** | 15% × $1,000 (ventas potenciales) | $150.00 USD |
| **Total pérdidas mensuales** | | **$290.00 USD** |
| **Total pérdidas anuales** | $290 × 12 | **$3,480.00 USD** |

> **Nota**: Estos valores son estimaciones conservadoras. En períodos de alta demanda (quincenas, fines de semana, festividades), las pérdidas por quiebre de stock pueden ser significativamente mayores.

### 3.3 Costos de Implementación de la Propuesta

| Componente | Costo Estimado | Tipo |
|------------|---------------|------|
| **Hardware** | | |
| Computadora/laptop para el servidor local | $0 (usa equipo existente) | Único |
| Servidor local (Raspberry Pi o similar, opcional) | $50 - $150 USD | Único |
| **Software** | | |
| Desarrollo del sistema (Python, FastAPI, Next.js) | $0 (desarrollado en la tesis) | Único |
| Licencias de software | $0 (Python, SQLite, framework open-source) | Recurrente |
| **Infraestructura** | | |
| Hosting local (computadora de la empresa) | $0 | Recurrente |
| Hosting en nube (opcional, si se requiere acceso remoto) | $5 - $15 USD/mes | Recurrente |
| **Mantenimiento** | | |
| Reentrenamiento periódico del modelo | $0 (automatizable) | Recurrente |
| Soporte técnico inicial (configuración) | $0 (desarrollado por el investigador) | Único |
| **Capacitación** | | |
| Capacitación al personal (3 empleados) | $0 (incluido en el proyecto) | Único |
| **Total inversión inicial** | **$50 - $150 USD** | |
| **Total costos recurrentes mensuales** | **$0 - $15 USD** | |

### 3.4 Beneficios Quantificables (Resultados de la Simulación)

Los resultados del backtesting (simulación retrospectiva a 90 días) demostraron:

| Indicador | Antes (Empírico) | Después (Sistema ML) | Mejora |
|-----------|-------------------|----------------------|--------|
| **Mermas por caducidad** | 12% mensual | **0%** (supresión total) | **100%** |
| **Quiebres de stock** | Frecuentes (15% ventas perdidas) | **Eliminados** | **100%** |
| **Precisión predictiva (MAPE)** | N/A (no existía pronóstico) | **8.5% - 12.4%** | Nuevo |
| **Lead time de respuesta** | 48-72 horas (reacción empírica) | **Tiempo real** (alertas automáticas) | Inmediato |

### 3.5 Proyección de Ahorro Anual

| Concepto | Ahorro Mensual | Ahorro Anual |
|----------|---------------|--------------|
| Eliminación de merma por caducidad | $60.00 | $720.00 |
| Eliminación de sobreproducción | $80.00 | $960.00 |
| Eliminación de ventas perdidas por stock | $150.00 | $1,800.00 |
| **Total ahorro anual** | **$290.00** | **$3,480.00** |

### 3.6 Relación Beneficio/Costo

| Métrica | Valor |
|---------|-------|
| **Inversión inicial** | $50 - $150 USD |
| **Costo anual operativo** | $0 - $180 USD |
| **Beneficio anual** | $3,480 USD |
| **ROI (Retorno de Inversión)** | **2,320% - 6,960%** |
| **Período de recuperación** | **< 1 mes** |
| **Beneficio neto anual** | **$3,300 - $3,480 USD** |

### 3.7 Beneficios No Cuantificables (Cualitativos)

| Beneficio | Descripción |
|-----------|-------------|
| **Mejora en calidad del producto** | Al usar insumos frescos (FIFO + predicción), la calidad de las tortas mejora |
| **Satisfacción del cliente** | Eliminación de quiebres de stock = pedidos siempre disponibles |
| **Seguridad alimentaria** | Menor acumulación de materia perecedera reduce riesgos sanitarios |
| **Toma de decisiones basada en datos** | La gerencia pasa de decidir "a ojo" a decidir con evidencia numérica |
| **Cumplimiento legal** | Art. 104 Ley de Soberanía Agroalimentaria: obligación de evitar desperdicio |
| **Escalabilidad** | El sistema puede ampliarse a otros productos o sucursales |
| **Ventaja competitiva** | Diferenciación frente a otras pastelerías de la zona |
| **Sostenibilidad ambiental** | Reducción del desperdicio de alimentos contribuye al medio ambiente |

### 3.8 Análisis de Riesgos de la Propuesta

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Fallo del modelo predictivo | Baja | Alto | Validación con Walk-Forward, métricas MAPE/RMSE |
| Resistencia del personal al cambio | Media | Medio | Capacitación, interfaz intuitiva (tablero de control) |
| Pérdida de datos históricos | Baja | Alto | Base de datos SQLite con respaldo automático |
| Obsolescencia del modelo | Media | Medio | Protocolo de reentrenamiento periódico (fine-tuning) |
| Dependencia de infraestructura | Baja | Medio | Arquitectura cliente-servidor, respaldo local |

### 3.9 Conclusión del Análisis Costo-Beneficio

La propuesta de implementar un sistema predictivo basado en Machine Learning para la optimización de inventarios perecederos en la Pastelería Casseríssima C.A. presenta:

1. **Viabilidad económica excepcional**: Con una inversión inicial mínima ($50-$150 USD) y costos operativos casi nulos, el sistema genera un ahorro anual estimado de $3,480 USD, lo que representa un retorno de inversión superior al 2,000%.

2. **Resultados comprobados**: La simulación retrospectiva (backtesting) demostró una reducción del 100% en mermas por caducidad y la eliminación completa de quiebres de stock para los insumos críticos.

3. **Factibilidad técnica**: El sistema utiliza tecnologías open-source (Python, FastAPI, SQLite, scikit-learn) que no generan costos de licenciamiento y son ampliamente soportadas.

4. **Impacto multidimensional**: Los beneficios trascienden lo económico e incluyen mejoras en calidad, seguridad alimentaria, cumplimiento legal y sostenibilidad ambiental.

5. **Escalabilidad**: La arquitectura modular permite ampliar el sistema a otros productos, categorías o incluso otras sucursales en el futuro.

---

*Documento generado como parte del análisis de la tesis "Sistema Predictivo basado en Machine Learning para la Optimización de Inventarios Perecederos de la Industria Repostera en la Pastelería Casseríssimas, Maturín, Estado Monagas"*

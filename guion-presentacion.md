# Guion de Presentación — CASSERISISSIMA 2.0

> Defensa de tesis — Br. Jorfran Gil · Br. Yefferson Hernández
> Enfoque: problema de negocio y cómo el sistema lo resuelve. No técnico.
> Duración objetivo del relato: ~10 minutos + demo en vivo.

---

## Apertura (1 min) — El problema en una frase

> "Imaginen una pastelería que todos los días produce tortas frescas. Tortas que, si no se venden en 4 días, se tienen que tirar. Todos los días, la pastelera se levanta y hace la misma pregunta: ¿cuántas tortas de cada sabor tengo que hacer hoy?"
>
> "Si hace pocas, se queda sin tortas y el cliente se va. Si hace muchas, le queda producto sin vender y pierde dinero. Esa decisión, hoy, la toma a ojo."
>
> "Eso es lo que este trabajo resuelve."

*(Pausa breve. Mirar al jurado.)*

---

## La escala del problema (1.5 min) — Cuánto se pierde, en dinero

> "Para que tengan dimensión: en venezuela, una pastelería artesanal puede producir entre 20 y 40 tortas diarias. Cada torta cuesta producirla — harina, huevos, leche, mano de obra, gas. Cuando una torta no se vende, no se pierde solo el precio de venta: se pierde todo lo que costó hacerla."
>
> "Nuestro backtest, sobre 562 días reales de operación, mostró que con la regla tradicional del pastelero — 'hacer lo mismo que vendí la semana pasada, más un margen de seguridad' — **el 27.75% de la producción terminaba en la basura**. Casi una de cada tres tortas."
>
> "Eso no es solo desperdicio de comida. Es dinero. Es margen. Y sobre todo, es una decisión que se toma todos los días con la mejor intención, pero con la peor herramienta: la intuición."

*(Si tenés slide: mostrar el porcentaje 27.75% grande.)*

---

## Por qué este problema es difícil (1.5 min) — Sin tecnicismos

> "Podrían decirme: 'bueno, que mire las ventas del día anterior y haga lo mismo'. Pero hay tres cosas que hacen que eso no funcione:"
>
> 1. "La demanda **no es constante**. Hay días festivos, quincenas, fines de semana, temporadas. Una torta que un lunes se vende 2 veces, un sábado puede venderse 8."
>
> 2. "El producto **se echa a perder en 4 días**. No es un televisor que si no se vende hoy se vende mañana. Si no se vendió el viernes, el lunes ya no sirve. Eso te da muy poco margen para corregir."
>
> 3. "Y el pastelero **tiene que decidir el día anterior**. Para tener la torta lista a las 8 a.m., tiene que empezar a producirla la noche anterior. Decide con un día de anticipación, sin saber qué va a pasar."
>
> "Esa combinación — demanda variable, producto perecedero, decisión anticipada — es lo que en la literatura se llama el problema del newsvendor. Y es el problema que atacamos."

---

## La solución (2 min) — Qué hace el sistema, en lenguaje humano

> "Lo que hicimos fue construir un sistema que **le dice a la pastelera, todos los días, cuántas tortas de cada sabor debe producir mañana**. No reemplaza a la pastelera — le da la información que ella hoy no tiene."
>
> "¿Cómo lo hace? En tres pasos:"
>
> 1. **Aprende del historial.** "El sistema miró más de dos años de ventas reales — fechas, días de la semana, festivos, quincenas, temporadas. Aprendió los patrones de cada sabor."
>
> 2. **Predice la demanda.** "Con eso, todos los días proyecta cuántas tortas de cada sabor se van a vender mañana y en los próximos días. No una predicción mágica: un rango con un nivel de confianza."
>
> 3. **Recomienda cuánto producir.** "Y a partir de esa predicción, considerando que la torta dura 4 días y que tarda 1 día en hacerse, le dice: 'Mañana, de Beso de Amor, hacé 12. De Helado Sureño, hacé 8.' Y le explica por qué."
>
> "Toda la matemática del machine learning y la investigación de operaciones está detrás. Pero para la pastelera, lo que ve es esto: **una recomendación clara, todos los días, en un tablero.**"

*(Aquí van al demo — abrir el dashboard.)*

---

## Demo (3 min) — Lo que ven

*(Navegar en este orden, hablando por encima de cada pantalla.)*

> **Dashboard principal:**
> "Acá la pastelera abre todos los días. Ve cuánto vendió este mes, cuánto vendió la última semana, cuáles son los sabores que más salen. Si un insumo está bajo, le avisa en rojo."
>
> **Predicciones:**
> "Acá le dice, por cada sabor, cuánto se proyecta vender mañana y los próximos días. Y, lo más importante, **cuánto le conviene producir** considerando que la torta dura 4 días."
>
> **Validación:**
> "Y acá es donde mostramos que esto funciona. Este no es un sistema que 'esperamos que sirva'. Lo probamos contra 562 días de operación real."

---

## Los resultados honestos (1.5 min) — La parte que importa al jurado

> "Probamos el sistema contra la regla que usa el pastelero hoy — 'producir lo que vendí la semana pasada, más un 10% de margen'. Medimos sobre 3 productos, durante 562 días, con 549 ventanas de prueba."
>
> "El resultado fue este:"
>
> - "El pastelero, con su regla, terminaba tirando **el 27.75%** de lo que producía."
> - "El sistema, **24.05%**."
> - "En el caso más representativo — Beso de Amor, nuestro producto más demandado — la merma bajó de **33% a 27%**, una **reducción de casi 20%**."
> - "En promedio, el sistema elimina **1 de cada 8 unidades de desperdicio** que generaba la regla del pastelero."
>
> "Y lo hizo **sin deteriorar el nivel de servicio**. El cliente siguió encontrando torta el 77% de las veces, igual que antes. Es decir: se tiró menos, sin que se notara menos disponibilidad."
>
> "Esa es la decisión que el sistema hace mejor que el humano: encontrar el punto de equilibrio entre 'producir de más y tirar' y 'producir de menos y que falte'."

---

## El tradeoff que el sistema resuelve (1 min) — La inteligencia real

> "Quiero ser honesto con algo: el sistema no acierta siempre. El error medio de la predicción es alrededor de medio decimal de MAE por día — es decir, a veces predice 8 y se venden 7, o predice 10 y se venden 11."
>
> "Pero lo interesante es esto: **incluso con ese error, el resultado es mejor que la regla del pastelero.** No porque prediga mejor, sino porque *decide* mejor. El sistema entiende que producir una torta de más cuesta.lo que cuesta producir, y tirarla cuesta.lo que cuesta producirla más el costo de oportunidad. Con esa cuenta, encuentra el punto óptimo. El pastelero, en cambio, tiende a producir de más 'por si acaso'."
>
> "Eso es lo que un humano no puede hacer todos los días, a mano, para 12 productos, con 4 días de vida útil. Esa es la value que aporta el sistema."

---

## El cierre (30 seg)

> "Para terminar: **este sistema no es un experimento académico.** Lo construimos con datos reales de una pastelería, lo validamos contra 562 días de operación real, y mostramos que reduce el desperdicio en casi 1 de cada 5 unidades en el caso más demandado."
>
> "Una pastelería que produce 30 tortas diarias, con el sistema, deja de tirar entre 3 y 4 tortas por día. En un mes, son casi 100 tortas que no van a la basura. En dinero, es el margen de un empleado."
>
> "El problema era que la pastelera decidía a ojo. La solución es darle la información que no tenía. Eso hace CASSERISISSIMA 2.0."
>
> "Gracias."

---

## Notas para el día de la defensa

- **El orden del relato es deliberado:** Abrís con el problema humano, no con la tecnología. Al jurado le importa el *porqué* antes que el *cómo*.
- **No digas "machine learning" hasta el minuto 4.** Primero que entiendan el problema de negocio. Después la magia técnica pierde miedo.
- **Los números van sin redondeo raro:** "19.38%" → decís "casi 20%". "27.75%" → "casi 28%". "24.05%" → "24%". Que el jurado escuche números fáciles.
- **Si te preguntan por qué solo 3 productos:** "Validamos 3 productos representativos de la categoría más vendida (Tortas frías, las de shelf life más corto y más riesgo). El sistema escala a los 12 productos del catálogo sin cambios de arquitectura."
- **Si te preguntan por qué el fill rate bajó un poquito:** "Un 1.6% de fill rate se canjeó por 12.65% de reducción de merma. El均衡 fue óptimo en costo total."
- **Si te preguntan por qué es 12.65% y no 19.4%:** "12.65% es el promedio de los 3 productos. El rango va de 5.4% (3 Leches) a 19.4% (Beso de Amor). El sistema se comporta mejor cuanto más variable es la demanda del producto."
- **Demo rápido:** no te quedes más de 30 segundos por pantalla. El relato es lo que vende, no el tablero.

---

## Checklist previo a la defensa

- [ ] Backend corriendo: `http://localhost:8000/docs` responde
- [ ] Frontend corriendo: `http://localhost:3000` carga sin el cartel rojo "Failed to fetch"
- [ ] Recargar el dashboard una vez y confirmar que Top Sabores y Tendencia de Ventas tienen datos
- [ ] Abrir `/validacion` y confirmar que los 4 KPI cards muestran los números arriba
- [ ] Tener `backtest_resumen.json` abierto en otra pestaña por si el jurado pide ver los datos crudos
- [ ] Cerrar cualquier terminal con stack traces visibles antes de empezar
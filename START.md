# PUENTE IA · PORTAL ÚNICO (Antigravity ↔ Copilot)

- **Guía rápida para Diego:** [guia.html](guia.html) · [GUIA_DIEGO.md](GUIA_DIEGO.md)
- **Referencia completa:** [PARA_COPILOT_LEEME.md](PARA_COPILOT_LEEME.md) · [HISTORIAL.md](HISTORIAL.md)

## INSTRUCCIONES OBLIGATORIAS PARA COPILOT (Protocolo 1.1)

1. **Si Diego continúa una tarea de Antigravity:** lee el bloque **Último traspaso / estado actual** de abajo y los archivos enlazados en `handoffs/<ID>/context/`. Usa `origin_mode: "reply_to_handoff"`.
2. **Si Diego empieza una tarea desde cero:** abre el proyecto en la tabla **Catálogo actual** (`ESTADO.md`, `estado.json`), lee obligatoriamente su `AGENTS.md` y todos los archivos reales afectados en `catalogo/<slug>/files/`. Usa el `commit` exacto de la tabla como `source_commit` y `origin_mode: "copilot_from_scratch"`.
3. **PROHIBIDO SUPONER O INVENTAR:** si algún enlace da error, no puedes leer un archivo o falta un requisito, **PARA antes de empezar** y pídele a Diego exactamente lo que te falta.
4. **Formato de entrega:** devuelve un ZIP `COPILOT_A_ANTIGRAVITY_<ID>.zip` con `HANDOFF.json` (`protocol_version` `1.1`, `task_id`, `direction: "copilot_to_antigravity"`, `origin_mode`, `project`, `repo_url`, `branch`, `source_commit`, `created_at`, `objective`, `files` con SHA-256 minúsculas), `RESPUESTA.md`, `PRUEBAS.md` y, si hay cambios, `PATCH.diff` y/o `files/` (`deleted_files` opcional). Prohibidos ejecutables binarios, scripts no declarados, `..`, rutas absolutas o secretos.

## Último traspaso / estado actual

# Traspaso a Copilot

- **ID:** 20261123-173818-estadisticas-033ac0
- **Modo:** `reply_to_handoff`
- **Proyecto:** estadisticas
- **Repositorio:** https://github.com/BioPeat/estadisticas.git
- **Rama:** main
- **Commit de origen:** `fb7a56a4efaeae13c9f73518518f73388ceb6a98`
- **Creado:** 2026-11-23T17:38:18.283181+00:00
- **Estado:** listo_para_copilot

## Objetivo

Corregir 6 problemas visuales/funcionales reportados por el usuario en capturas móviles (cabecera del acta solapada, selector Totales/Por partido en Reparto de puntos, gráficas de dos líneas más altas y legibles, enlaces de Lector multiusuario vs Editor individual, botón Pegar del portapapeles en editor de mapa de tiro, rediseño de paletas no rojas y eliminación de colores rojo/azul fijos fuera de la paleta roja) + 3 pulidos adicionales detectados en las mismas vistas.

## Qué se ha hecho

Se han revisado las 10 capturas móviles del usuario y se ha localizado en el código actual (commit fb7a56a) la causa raíz exacta de cada punto:
1. Cabecera acta (app.js:1246, styles.css:240-244,357,724): <th class="identity" rowspan="2">N.º jugadora · Nombre</th> tiene white-space:nowrap con max-width:112px en móvil y font-size:11px sin overflow:hidden ni salto de línea, invadiendo visualmente la columna MIN.
2. Reparto de puntos (app.js:682-687,995,1283-1288): la tarjeta usa Vista rápida fija solo con totales, a diferencia de Minutos (app.js:108,689-700,852-856,1795) que tiene selector #minutesScope.
3. Gráficas de dos líneas (app.js:787-806, styles.css:478,523,650,689): dualTrendSVG en modo compacto usa viewBox 760x116 (relación 6,55:1) dentro de tarjetas estrechas de 2 columnas con altura 62-70px y min=Math.min(0,...valid), por lo que en móvil el dibujo real ocupa ~23px de alto y ambas líneas salen casi pegadas.
4. Compartir equipo (worker.js:76-84,128-130; app.js:1681,1706-1716,1824-1833): actualmente team_access_tokens valida solo token_hash sin vincular dispositivo, así que tanto viewer como editor se pueden abrir en varios dispositivos, mientras la UI dice "Crea un enlace para cada persona".
5. Editor mapa de tiro (app.js:1456,1814): el paso 2 solo tiene <textarea id="shotJson"> y botón "Leer y colocar"; falta un botón para pegar del portapapeles.
6. Paletas y fugas de rojo/azul (app.js:11-12; styles.css:80-82,228-249,464-465,603,658-668): PALETTES.blue/teal/purple usan combinaciones estridentes; además .balance-mini i.positive/.negative (styles.css:603) siguen hardcodeadas a var(--red)/var(--blue) (afectando a Diferencia, pestaña Comparar y Parcial por cuarto), .share-bars usa linear-gradient(var(--purple),var(--red)), .minute-bars usa linear-gradient(var(--blue),var(--green)), .stacked-chart usa --red/--blue/--green y .boxscore/.team-tabs usan --blue.
Extras detectados en las capturas:
- En scoreChart (app.js:656-662), en el primer partido (P1) cuando los puntos están cerca, el desplazamiento ux=x-15 hace que la etiqueta numérica se solape con el texto "máx ..." de axis-label.
- En renderShotQuartersEditor (app.js:1437+), los placeholders de los inputs de parciales repiten el nombre largo del equipo y se cortan en móvil cuando la cabecera de columnas ya indica los equipos.
- En Ajustes (app.js:1681), el selector de Color propio no muestra vista previa visual del par de colores.

## Qué falta

Implementar los 6 requisitos y mejoras de pulido en app.js, styles.css, worker.js y pruebas (tests/worker_mock.mjs, tests/smoke.py si aplica):
1. Cabecera del acta (boxscore): corregir el solape de "N.º jugadora · Nombre" / "N.º jugador · Nombre" en móvil y desktop. Permitir salto de línea controlado (white-space:normal; line-height:1.2; overflow:hidden; vertical-align:middle) y/o texto limpio en 2 líneas o etiqueta compacta respetando género (genderTerms()), verificando que nunca invada la columna MIN ni pierda sticky left:0 / z-index:9.
2. Reparto de puntos con Totales y Por partido: añadir estado pointShareScope ('season' | 'average', y opcionalmente partidos concretos o selector limpio equivalente al de Minutos con id="pointShareScope"), resetearlo al cambiar/crear/restaurar equipo igual que minutesScope. Actualizar renderTeam() y pointShareChart() para mostrar totales (pts y % del equipo) o media por partido jugado (pts/gp con 1 decimal, ordenando por media; sin fila "Resto" engañosa en modo por partido). Soportar también Totales / Por partido dentro del modal openPointShareDetail().
3. Gráficas duales de estadísticas de equipo más amplias y claras: rediseñar dualTrendSVG(..., compact=true) para que aproveche de verdad el espacio vertical de cada tarjeta sin solaparse con cabecera ni "Ver detalle ->". Usar un viewBox compacto proporcionado al ancho real de tarjeta (ej. 220x104 en vez de 760x116), aumentar la altura de .dual-trend.compact y .metric-evolution (ej. ~90-100px), ajustar el rango Y en modo compacto con padding moderado alrededor de [minVal, maxVal] (en lugar de forzar siempre min=0 cuando aplasta las dos líneas), mantener pequeña separación si coinciden ambos valores y asegurar que los círculos y trazos queden nítidos y bien contenidos.
4. Compartir equipo (Lector multiusuario vs Editor individual):
   - Lector (viewer): debe poder abrirse y usarse por múltiples personas/dispositivos con un único enlace compartido para toda la plantilla.
   - Editor (editor): debe ser individual (vinculado a 1 dispositivo/persona). Implementar en worker.js (migración aditiva versionada subiendo SCHEMA_VERSION a 4 usando addColumn tolerante: bound_client_id TEXT y bound_at TEXT en team_access_tokens; añadir X-Client-Id a Access-Control-Allow-Headers en responseHeaders!). En app.js generar/persistir un clientId estable en localStorage (ej. estadisticas_client_id) y enviarlo como cabecera X-Client-Id en las llamadas autenticadas del equipo. En teamAuth() para role==='editor': si llega X-Client-Id, vincular atómicamente en el primer uso (UPDATE ... WHERE id=? AND bound_client_id IS NULL) y rechazar con 403 claro si ya está vinculado a otro X-Client-Id (o si falta X-Client-Id cuando ya está vinculado). Dejar intacto el comportamiento multiusuario de viewer y todas las rutas/tablas legacy w2. Exponer bound_at en GET /api/v3/teams/:id/invites y actualizar el copy de openSettings() y loadInvites() en app.js para explicar claramente: Lector = compartible con todo el equipo; Editor = individual (1 dispositivo), indicando en la lista si está "En uso" o "Sin usar". Manejar el error 403 en app.js con un mensaje claro al usuario.
5. Botón "Pegar del portapapeles" en editar mapa de tiro: añadir un botón junto a "Leer y colocar" (p. ej. data-action="paste-shot-json", texto "Pegar del portapapeles") que lea navigator.clipboard.readText(), rellene #shotJson y avise con toast; con fallback claro si el navegador deniega permiso de portapapeles (enfocando #shotJson e indicando pegar manualmente).
6. Paletas de colores y eliminación de rojo/azul hardcodeados:
   - Dejar PALETTES.red EXACTAMENTE igual: light:['#C6283D','#1E5F9E'], dark:['#FF6B78','#7CC4FF'].
   - Rediseñar las demás paletas (manteniendo las claves 'blue', 'teal', 'purple' por compatibilidad con equipos existentes, y opcionalmente añadiendo alguna más si aporta valor) para que sean elegantes, editoriales, deportivas y armónicas entre [propio, rival] con contraste WCAG AA en modo claro y oscuro (inspiradas en la sobriedad de la paleta roja, evitando combinaciones estridentes como morado neón + marrón o verde + violeta chillón).
   - Auditar todo styles.css para que ninguna tarjeta/gráfico comparativo de equipo muestre rojo+azul fijos cuando se usa otra paleta: en particular actualizar .balance-mini i.positive/.negative a var(--team)/var(--rival) (arregla Diferencia, pestaña Comparar y Parcial por cuarto), armonizar .share-bars, .minute-bars, .stacked-chart (2P/3P/TL) y acentos del acta (.team-tabs button.active, .boxscore thead th, .boxscore td.identity b) con la identidad del equipo sin romper la regla de ficha individual sin color por columna ni quitar el rojo semántico de alertas/errores/zona peligrosa/derrotas.
7. Extras de pulido detectados en capturas:
   - Evitar que en scoreChart (P1) el número del primer partido se solape con la etiqueta "máx ..." de axis-label.
   - En los inputs de parciales por cuarto del editor de mapa, usar placeholders cortos/limpios (ej. "0" o "Pts") para evitar textos cortados.
   - En Ajustes, añadir vista previa visual (swatches con el par equipo/rival) al selector de paleta de color.

## Archivos de contexto

- [context/AGENTS.md](context/AGENTS.md) — `181b885ccc12910d28783326b0bd91a884253ce9b470aef790608b46e38f6c5a`
- [context/CONTEXTO_ESTADISTICAS.md](context/CONTEXTO_ESTADISTICAS.md) — `ba922ceb46bb1c709fc03bab5e094831ad60680b62df392b736ee173ccba63a1`
- [context/MAPA_DEL_CODIGO.md](context/MAPA_DEL_CODIGO.md) — `bccd2d4f2dfe246a7f4910ec992c04b9a9454fddf66ca22c12e473753a60d779`
- [context/index.html](context/index.html) — `5214a4f2ff2d39b2a01a381205f22245990cdaa5860ba06bcdd0a8f9613d593e`
- [context/styles.css](context/styles.css) — `6bd65c7d8a1ef608baf3d84280151454a0370585ba8c4484186c5c19e2e08da9`
- [context/app.js](context/app.js) — `10abf210b3a65e9027fcb5004fef94399867e3067760b32103a0916d18816975`
- [context/worker.js](context/worker.js) — `77e86b9000029ad302295395b8fdf1828b4f4f90bd0081ff55e5c82252f0d919`
- [context/tests/worker_mock.mjs](context/tests/worker_mock.mjs) — `3fc97d64c2b3662907e220b6c66b2b2b8b8e20b508db3e6c2f8f87ffbc031bdb`
- [context/tests/smoke.py](context/tests/smoke.py) — `98967d6e60d1ae776254abb231573d5f724c755fad89e41c8f0e175bcd7c59c3`
- [context/tools/validate.py](context/tools/validate.py) — `4b187b8569ef466bad89ceb347d844826387ec0e0d7b0345b47e5832e9910dd1`

## Pruebas ejecutadas y resultado

Antes de este traspaso no se han modificado archivos del repositorio. Al volver el ZIP, Antigravity ejecutará: py tools/validate.py, node tests/worker_mock.mjs, py tests/smoke.py (incluido Pozuelo), py tests/updater_e2e.py y verificación visual en navegador móvil/desktop.

## Decisiones y restricciones

Reglas obligatorias de AGENTS.md y arquitectura:
- Conservar STORE='estadisticas_shared_v2' y MULTI_STORE='estadisticas_multiteam_v11'.
- No renombrar ni borrar rutas/tablas w2. No recrear D1 y no pedir /api/setup en actualizaciones.
- Migraciones del Worker: estrictamente aditivas, versionadas (SCHEMA_VERSION=4) y tolerantes a columnas existentes vía addColumn().
- Si el cliente envía una cabecera nueva como X-Client-Id, añadirla obligatoriamente a Access-Control-Allow-Headers en worker.js (responseHeaders) para no romper CORS en GitHub Pages.
- Mantener claves existentes de PALETTES ('red', 'blue', 'teal', 'purple') y dejar PALETTES.red intacta.
- Mantener género, aislamiento por workspace/teamId y la ficha individual sin color por columna.
- No tocar ni entregar assets/ ni el logo data-logo="aro-vector". No sobrescribir AGENTS.md.
- Directo ausente sigue siendo hueco/null, nunca cero.
- Actualizar tests/worker_mock.mjs para cubrir: (a) enlace viewer utilizable desde varios X-Client-Id, (b) enlace editor vinculado al primer X-Client-Id y rechazado con 403 desde un segundo X-Client-Id, (c) compatibilidad w2 intacta.
- No incluir secretos, tokens ni datos personales en código, tests o respuestas.

## Pregunta concreta para Copilot

Implementa los 6 cambios solicitados más los 3 pulidos detectados y entrega el paquete ZIP compatible con Puente IA 1.1 (HANDOFF.json, RESPUESTA.md, PRUEBAS.md y files/ o PATCH.diff) listo para que Antigravity lo valide, ejecute toda la batería de pruebas (validate, worker_mock, smoke, updater_e2e) y lo publique. Si necesitas confirmar si el despliegue de worker.js en Cloudflare queda pendiente tras el push de GitHub Pages, indícalo claramente en PRUEBAS.md.

## Regla de entrega

Responder con `COPILOT_A_ANTIGRAVITY_20261123-173818-estadisticas-033ac0.zip` incluyendo `HANDOFF.json` (`protocol_version`: `1.1`, `direction`: `copilot_to_antigravity`, `origin_mode`: `reply_to_handoff`, `source_commit`: `fb7a56a4efaeae13c9f73518518f73388ceb6a98`), `RESPUESTA.md`, `PRUEBAS.md` y, si hay cambios, `PATCH.diff` y `files/`.

## Catálogo actual de repositorios públicos

| Proyecto | Visibilidad | Commit actual (`source_commit`) | Enlaces directos |
|---|---|---|---|
| biopeat | Público | `1c21adb8a651c19771ea4ebe6ee49def9243971b` | [ESTADO.md](catalogo/biopeat/ESTADO.md) · [resumen.html](catalogo/biopeat/resumen.html) · [estado.json](catalogo/biopeat/estado.json) · [AGENTS.md](catalogo/biopeat/files/AGENTS.md) |
| Finanzas | Público | `9cb8b81621da18cfbf4a558c5cd64fb7bb1e3b47` | [ESTADO.md](catalogo/finanzas/ESTADO.md) · [resumen.html](catalogo/finanzas/resumen.html) · [estado.json](catalogo/finanzas/estado.json) · [AGENTS.md](catalogo/finanzas/files/AGENTS.md) |
| estadisticas | Público | `1c052b27c3c1dd6cba07f065e140981caae2a531` | [ESTADO.md](catalogo/estadisticas/ESTADO.md) · [resumen.html](catalogo/estadisticas/resumen.html) · [estado.json](catalogo/estadisticas/estado.json) · [AGENTS.md](catalogo/estadisticas/files/AGENTS.md) |

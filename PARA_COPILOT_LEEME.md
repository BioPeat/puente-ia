# PARA COPILOT (OPUS 5.5) · LÉEME PRIMERO (Puente IA v1.1.0)

Hola, Copilot. Soy **Antigravity (Gemini Neon)**. Ya he auditado, corregido, instalado y probado tu kit v1.0.0 en el portátil personal de Diego, elevándolo a **v1.1.0 (`Protocolo 1.1`)** en el repositorio público `BioPeat/puente-ia`.

---

## 1. Resumen de mi auditoría sobre tu v1.0.0

### En qué coincido contigo
- Arquitectura híbrida **GitHub público + PairDrop + ZIP con SHA-256** (coste 0 €, sin instalar nada en el portátil del trabajo y sin exponer datos privados).
- Validaciones estrictas anti ZIP-Slip, rechazo de binarios/scripts no declarados, bloqueo de secretos, control de `source_commit` y verificación de `origin`.
- Registro dinámico de proyectos en `config.json` para soportar cualquier repositorio futuro sin tocar la skill.

### Errores y carencias encontrados en v1.0.0 y corregidos en v1.1.0
1. **Ruta global de skill incorrecta**: en v1.0.0 se indicaba `%USERPROFILE%\.gemini\antigravity\skills\copilot-bridge\`, ruta legacy que la app principal de Antigravity no carga. La ruta oficial actual en Antigravity es `%USERPROFILE%\.gemini\config\skills\copilot-bridge\`, ya instalada ahí.
2. **Faltaba cubrir el Sentido 2 (`Copilot -> Antigravity` desde cero)**: tu diseño resolvía bien la vuelta de una tarea iniciada en Antigravity, pero no te daba el estado vivo ni copias legibles de los repos cuando Diego te pide una tarea desde cero (y cuando GitHub directo falla o da 404). En v1.1.0 se añade:
   - `catalogo/` con copia legible de los archivos de texto públicos de cada repo, su `ESTADO.md`, `estado.json` (`source_commit` real) y `resumen.html`, además de sincronización automática por GitHub Actions (`sync-catalogo.yml`) y comando local `sync-repos`.
   - `origin_mode: "copilot_from_scratch"` en `HANDOFF.json` y soporte completo en `record-result` sin requerir traspaso previo en `handoffs/`.
3. **GitHub Pages en `/docs` dejaba fuera `handoffs/` y `catalogo/`**: se ha activado GitHub Pages en la **raíz `/` de `main`** (con `.nojekyll` y `robots.txt` `Disallow: /`), exponiendo `ULTIMO_TRASPASO.md`, `ultimo.html`, `CATALOGO.md`, `catalogo.html`, `handoffs/` y `catalogo/` por **3 canales redundantes**.
4. **Falso positivo crítico en `bridge_tool.py`**: la regex `-----BEGIN ... PRIVATE KEY-----` rechazaba `Finanzas/js/connectors.js` (placeholder HTML) y `Finanzas/worker.js` (validador de formato). Ahora exige cabecera + salto de línea + cuerpo Base64 real (`>= 32` chars).
5. **Endurecimiento de `bridge_tool.py`**:
   - Escaneo de todo el árbol extraído del ZIP (no solo desde `locate_package_root`), evitando archivos ocultos fuera de subcarpetas.
   - Extracción por streaming con límite real de bytes (`100 MB`) contra ZIP bombs con cabecera manipulada.
   - Detección añadida de claves Google (`AIza...`), AWS (`AKIA...`) y fugas de rutas locales de usuario Windows (`Users/<cuenta>`). Se excluyen metadatos de máquina local como `.agents/REGISTRO_CONFIG_ANTIGRAVITY.md` al sincronizar `catalogo/`.
   - Normalización de `repo_url` insensible a `.git` final y a mayúsculas en `owner/repo` (`BioPeat/Finanzas`).
   - Comandos completos añadidos: `sync-repos`, `find-zip`, `check-target`, `apply` (con copia de recuperación previa), `record-result` y `deleted_files` opcional.

---

## 2. Tus enlaces fijos (3 canales alternativos)

Si un canal te falla o te da error/404 desde tu entorno, prueba los otros dos en este orden:

### A) Para leer esta guía (`PARA_COPILOT_LEEME.md`)
1. GitHub Pages: https://biopeat.github.io/puente-ia/PARA_COPILOT_LEEME.md
2. Raw GitHub: https://raw.githubusercontent.com/BioPeat/puente-ia/main/PARA_COPILOT_LEEME.md
3. Web GitHub: https://github.com/BioPeat/puente-ia/blob/main/PARA_COPILOT_LEEME.md

### B) Sentido 1 · Leer el último traspaso de Antigravity (`Antigravity -> Copilot`)
1. GitHub Pages (HTML legible): https://biopeat.github.io/puente-ia/ultimo.html
2. Raw GitHub (Markdown): https://raw.githubusercontent.com/BioPeat/puente-ia/main/ULTIMO_TRASPASO.md
3. Web GitHub: https://github.com/BioPeat/puente-ia/blob/main/ULTIMO_TRASPASO.md
4. Estado JSON directo: https://biopeat.github.io/puente-ia/estado.json (o `https://raw.githubusercontent.com/BioPeat/puente-ia/main/estado.json`)

### C) Sentido 2 · Empezar una tarea desde cero (`Copilot -> Antigravity`)
1. Índice del catálogo (HTML): https://biopeat.github.io/puente-ia/catalogo.html
2. Índice del catálogo (Markdown Raw): https://raw.githubusercontent.com/BioPeat/puente-ia/main/CATALOGO.md
3. Índice JSON (commits actuales): https://biopeat.github.io/puente-ia/catalogo.json
4. Estado y archivos de cada repo público (`<slug>` = `biopeat`, `finanzas`, `estadisticas`, o cualquier futuro):
   - Resumen HTML: `https://biopeat.github.io/puente-ia/catalogo/<slug>/resumen.html`
   - Estado JSON (`commit` + lista de archivos): `https://biopeat.github.io/puente-ia/catalogo/<slug>/estado.json`
   - Archivo individual Raw: `https://raw.githubusercontent.com/BioPeat/puente-ia/main/catalogo/<slug>/files/<ruta_relativa>`
   - Archivo individual Pages: `https://biopeat.github.io/puente-ia/catalogo/<slug>/files/<ruta_relativa>`

---

## 3. Reglas obligatorias para ti en Protocolo 1.1

1. **PROHIBIDO SUPONER O INVENTAR**:
   - Antes de diseñar o generar código en cualquier sentido (especialmente en **Sentido 2 desde cero**), lee obligatoriamente `AGENTS.md` del proyecto destino, el `commit` exacto (`source_commit`) y todos los archivos reales afectados desde `catalogo/<slug>/files/...` (o desde `handoffs/<ID>/context/...`).
   - Si no puedes abrir las URLs (404/bloqueo), si un archivo pesa >2 MB y fue omitido (revisa `omitted` en `estado.json`), o si te falta un dato o requisito funcional: **PARA antes de empezar** y dile a Diego exactamente qué archivo(s) o aclaración necesitas (por PairDrop o en texto).
2. **Formato de entrega ZIP (`COPILOT_A_ANTIGRAVITY_<ID>.zip`)**:
   - `HANDOFF.json`:
     - `protocol_version`: `"1.1"` (también aceptamos `"1.0"`)
     - `task_id`: el del traspaso en Sentido 1, o uno nuevo `YYYYMMDD-HHMMSS-<slug>-<hex6>` (mínimo 8 caracteres, `[A-Za-z0-9._-]`) en Sentido 2
     - `direction`: `"copilot_to_antigravity"`
     - `origin_mode`: `"reply_to_handoff"` (Sentido 1) o `"copilot_from_scratch"` (Sentido 2)
     - `project`, `repo_url`, `branch`, `source_commit` (exacto leído del traspaso o `catalogo/<slug>/estado.json`), `created_at`, `objective`
     - `files`: lista `{ "path": "...", "sha256": "<hex minúsculas>" }` cubriendo **cada** archivo en `files/`, `PATCH.diff` (si existe), `PRUEBAS.md` (y cualquier script fuente legítimo del repo que modifiques)
     - `deleted_files` (opcional): lista de rutas relativas a borrar si procede
   - `RESPUESTA.md` (resumen claro en español + fuentes exactas que leíste)
   - `PRUEBAS.md` (qué comprobaste y qué debe ejecutar Antigravity en local)
   - `PATCH.diff` (diff unificado Git limpio) y/o `files/<ruta_relativa>` (archivos completos modificados). Si incluyes ambos, asegúrate de que coinciden exactamente byte a byte.
3. **Qué NO puedes incluir jamás en el ZIP ni pedir que se ejecute**:
   - Ejecutables binarios (`.exe`, `.msi`, `.dll`, `.com`, `.scr`, etc.), enlaces simbólicos, rutas `..` o absolutas, scripts no declarados en `files`, secretos, tokens, `.env`, claves privadas, datos reales de usuario ni rutas locales de Windows.
   - Antigravity nunca ejecutará scripts del ZIP; siempre validará hashes, comparará `source_commit`, aplicará en local y correrá la suite oficial del repo (`smoke.py`, `worker_smoke.mjs`, `check-static.mjs`, navegador, etc.).

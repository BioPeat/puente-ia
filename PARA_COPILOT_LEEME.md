# PARA COPILOT (OPUS 5.5) · LÉEME PRIMERO (Puente IA v1.2.0)

Hola, Copilot. Soy **Antigravity (Gemini Neon)**. Tu punto de entrada único a partir de ahora es el portal **todo-en-uno**:

- **Portal único (Pages):** https://biopeat.github.io/puente-ia/
- **Portal único (Markdown Raw):** https://raw.githubusercontent.com/BioPeat/puente-ia/main/START.md
- **Portal único (GitHub web):** https://github.com/BioPeat/puente-ia/blob/main/START.md

En ese único enlace ya aparecen siempre: las instrucciones del protocolo, el **último traspaso** (`Sentido 1`) y el **catálogo actual de apps públicas** con su commit exacto y archivos (`Sentido 2`).

---

## 1. Resumen de mi auditoría sobre tu v1.0.0 → v1.2.0

### En qué coincido contigo
- Arquitectura híbrida **GitHub público + PairDrop + ZIP con SHA-256** (coste 0 €, sin instalar nada en el portátil del trabajo y sin exponer datos privados).
- Validaciones anti ZIP-Slip, rechazo de binarios/scripts no declarados, bloqueo de secretos, control de `source_commit` y verificación de `origin`.
- Registro dinámico de proyectos en `config.json` para cualquier repositorio futuro.

### Errores y carencias encontrados en v1.0.0 y corregidos
1. **Ruta global de skill incorrecta**: en v1.0.0 se indicaba `%USERPROFILE%\.gemini\antigravity\skills\copilot-bridge\`, ruta legacy que la app principal de Antigravity no carga. La ruta oficial es `%USERPROFILE%\.gemini\config\skills\copilot-bridge\`, ya instalada ahí.
2. **Faltaba cubrir el Sentido 2 (`Copilot -> Antigravity` desde cero)**: en v1.1/v1.2 se añade `catalogo/` con copia legible de los archivos de texto públicos de cada repo, su `ESTADO.md`, `estado.json` (`source_commit` real), sincronización automática gratuita vía GitHub Actions (`sync-catalogo.yml`) y soporte `origin_mode: "copilot_from_scratch"` en `record-result`.
3. **GitHub Pages en `/docs` dejaba fuera `handoffs/` y `catalogo/`**: ahora GitHub Pages sirve la **raíz `/` de `main`** (con `.nojekyll` y `robots.txt` `Disallow: /`).
4. **Falso positivo crítico en `bridge_tool.py`**: la regex `-----BEGIN ... PRIVATE KEY-----` bloqueaba `Finanzas/js/connectors.js` (placeholder HTML) y `Finanzas/worker.js` (validador). Ahora exige cabecera + salto de línea + cuerpo Base64 real (`>= 32` chars).
5. **Simplificación máxima en v1.2.0**: portal todo-en-uno (`index.html` y `START.md`) con instrucciones incrustadas para que Diego no copie texto técnico, guía visual `guia.html`, órdenes cortas (`PUENTE: pásalo a Copilot`, `PUENTE: aplica lo de Copilot`, `PUENTE: añade <URL>`) y archivado automático `archive-zip` en `Descargas/Puente-IA-procesados/`.
6. **Endurecimiento de `bridge_tool.py`**: escaneo de todo el árbol extraído del ZIP, extracción por streaming con límite real de 100 MB, validación de rutas en `PATCH.diff` y `deleted_files`, detección de claves Google/AWS y bloqueo de rutas locales Windows (`Users/<cuenta>`), excluyendo `.agents/REGISTRO_CONFIG_ANTIGRAVITY.md` al sincronizar el catálogo.

---

## 2. Enlaces fijos (3 canales alternativos)

- **Portal todo-en-uno (recomendado siempre):**
  1. `https://biopeat.github.io/puente-ia/`
  2. `https://raw.githubusercontent.com/BioPeat/puente-ia/main/START.md`
  3. `https://github.com/BioPeat/puente-ia/blob/main/START.md`
- **Último traspaso suelto:** `ultimo.html` / `ULTIMO_TRASPASO.md` / `estado.json`
- **Catálogo suelto:** `catalogo.html` / `CATALOGO.md` / `catalogo.json`
- **Por app (`<slug>` = `biopeat`, `finanzas`, `estadisticas`, ...):**
  - `catalogo/<slug>/resumen.html` · `catalogo/<slug>/ESTADO.md` · `catalogo/<slug>/estado.json` · `catalogo/<slug>/files/<ruta>`

---

## 3. Reglas obligatorias para ti en Protocolo 1.1

1. **PROHIBIDO SUPONER O INVENTAR**: lee siempre `AGENTS.md` del proyecto destino, el `source_commit` real y los archivos afectados antes de proponer cambios. Si falla un enlace, falta un archivo (>2 MB omitido) o falta un requisito, **PARA antes de empezar** y pídeselo a Diego.
2. **Formato de entrega (`COPILOT_A_ANTIGRAVITY_<ID>.zip`)**:
   - `HANDOFF.json`: `protocol_version` `"1.1"`, `task_id` (>=8 chars), `direction: "copilot_to_antigravity"`, `origin_mode` (`"reply_to_handoff"` | `"copilot_from_scratch"`), `project`, `repo_url`, `branch`, `source_commit`, `created_at`, `objective`, `files` (`path`, `sha256` minúsculas), `deleted_files` opcional.
   - `RESPUESTA.md`, `PRUEBAS.md` y, si hay cambios, `PATCH.diff` y/o `files/` (coincidiendo byte a byte si van ambos).
3. **Prohibido**: binarios ejecutables, symlinks, rutas `..` o absolutas, scripts no declarados en `files`, secretos o rutas locales Windows.

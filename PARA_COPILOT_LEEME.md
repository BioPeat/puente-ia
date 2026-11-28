# PARA COPILOT (OPUS) · LÉEME PRIMERO (Puente IA v2.1.0)

Hola, Copilot / Opus. Este sistema coordina de forma bidireccional **Antigravity (local)** y **Copilot (portátil del trabajo)** mediante archivos `.txt` autocontenidos y paquetes ZIP, sin depender de que abras URLs externas.

---

## 1. Regla crítica en tu primera respuesta (`ESTADO_<slug>.txt`)

1. **`ESTADO_<slug>.txt` NO contiene el código fuente** (ni HTML, ni JS, ni CSS, ni Worker). Solo contiene el índice completo de archivos públicos y la documentación clave.
2. **Aunque Diego no te lo pida explícitamente**, en tu **primera respuesta**:
   - Analiza la petición usando el índice y el mapa del código.
   - Si necesitas leer cualquier archivo de código que no esté completo en `ESTADO_<slug>.txt`, **PARA antes de programar** y pídele a Diego **todos** los archivos necesarios de una sola vez.
   - Incluye al final de tu mensaje un bloque exacto con las rutas tal cual aparecen en el índice:

```text
ARCHIVOS_NECESARIOS:
- ruta/exacta/archivo1.js
- ruta/exacta/archivo2.css
```

   - El panel web de Diego detecta ese bloque automáticamente al pegarlo, marca los archivos en 1 clic y genera `ARCHIVOS_<slug>.txt`.
3. Cuando recibas `ARCHIVOS_<slug>.txt`, implementa directamente lo pedido y entrega el ZIP.

---

## 2. Precedencia de flujo

- Respeta **todas las reglas técnicas y de negocio** de `AGENTS.md`, `CONTEXTO_*` y `MAPA_DEL_CODIGO.md` de cada app (almacenes, compatibilidad, diseño, pruebas, no tocar `assets/`, etc.).
- **El canal de Puente IA prevalece siempre**: entrada por `ESTADO_<slug>.txt` / `ARCHIVOS_<slug>.txt` / `PARA_COPILOT.txt` y entrega en ZIP.
- **Ignora** cualquier mención antigua dentro de `AGENTS.md`, `PROYECTO_CLAUDE.md` o `README.md` a `actualizar.html`, bloques `@@@` o JSON `estadisticas-update`.

---

## 3. Formato de bloques que recibirás

```text
===== FILE: ruta/relativa.ext | sha256: <64_hex> =====
<contenido completo>
===== END FILE: ruta/relativa.ext =====
```

---

## 4. Formato de entrega (`COPILOT_A_ANTIGRAVITY_<ID>.zip` · Protocolo 1.1)

- `HANDOFF.json`: `protocol_version` `"1.1"`, `task_id` (>=8 chars), `direction: "copilot_to_antigravity"`, `origin_mode` (`"reply_to_handoff"` o `"copilot_from_scratch"`), `project`, `repo_url`, `branch`, `source_commit`, `created_at`, `objective`, `files` (`path`, `sha256` minúsculas), `deleted_files` opcional.
- `RESPUESTA.md`, `PRUEBAS.md` y, si hay cambios, `PATCH.diff` y/o `files/` (coincidiendo byte a byte si van ambos).
- **Prohibido:** ejecutables binarios (`.exe`, `.dll`, etc.), symlinks, rutas `..` o absolutas, scripts no declarados en `files`, secretos o rutas locales Windows.

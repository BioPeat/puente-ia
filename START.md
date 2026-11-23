# PUENTE IA · PORTAL ÚNICO (Antigravity ↔ Copilot)

- **Guía rápida para Diego:** [guia.html](guia.html) · [GUIA_DIEGO.md](GUIA_DIEGO.md)
- **Referencia completa:** [PARA_COPILOT_LEEME.md](PARA_COPILOT_LEEME.md) · [HISTORIAL.md](HISTORIAL.md)

## INSTRUCCIONES OBLIGATORIAS PARA COPILOT (Protocolo 1.1)

1. **Si Diego continúa una tarea de Antigravity:** lee el bloque **Último traspaso / estado actual** de abajo y los archivos enlazados en `handoffs/<ID>/context/`. Usa `origin_mode: "reply_to_handoff"`.
2. **Si Diego empieza una tarea desde cero:** abre el proyecto en la tabla **Catálogo actual** (`ESTADO.md`, `estado.json`), lee obligatoriamente su `AGENTS.md` y todos los archivos reales afectados en `catalogo/<slug>/files/`. Usa el `commit` exacto de la tabla como `source_commit` y `origin_mode: "copilot_from_scratch"`.
3. **PROHIBIDO SUPONER O INVENTAR:** si algún enlace da error, no puedes leer un archivo o falta un requisito, **PARA antes de empezar** y pídele a Diego exactamente lo que te falta.
4. **Formato de entrega:** devuelve un ZIP `COPILOT_A_ANTIGRAVITY_<ID>.zip` con `HANDOFF.json` (`protocol_version` `1.1`, `task_id`, `direction: "copilot_to_antigravity"`, `origin_mode`, `project`, `repo_url`, `branch`, `source_commit`, `created_at`, `objective`, `files` con SHA-256 minúsculas), `RESPUESTA.md`, `PRUEBAS.md` y, si hay cambios, `PATCH.diff` y/o `files/` (`deleted_files` opcional). Prohibidos ejecutables binarios, scripts no declarados, `..`, rutas absolutas o secretos.

## Último traspaso / estado actual

# Resultado de importación y cierre

- **ID:** 20261123-171428-finanzas-804f4d
- **Modo de origen:** `copilot_from_scratch`
- **Proyecto:** Finanzas
- **Repositorio:** https://github.com/BioPeat/Finanzas.git
- **Rama:** main
- **Commit de origen:** `9cb8b81621da18cfbf4a558c5cd64fb7bb1e3b47`
- **Commit final:** `9cb8b81621da18cfbf4a558c5cd64fb7bb1e3b47`
- **Estado:** `completed`
- **Registrado (UTC):** 2026-11-23T17:17:46.134422+00:00

## Resumen

Primer ciclo real Copilot desde cero -> Antigravity verificado sin cambios en Finanzas.

## Pruebas ejecutadas en Antigravity

validate OK, check-target OK (origin y commit exactos), git status limpio en Finanzas.

## Notas

Copilot verificó 4/4 hashes de ESTADO_finanzas.txt y detectó diferencia CRLF/LF; corregido en v2.0.1 del puente.

## Catálogo actual de repositorios públicos

| Proyecto | Visibilidad | Commit actual (`source_commit`) | Enlaces directos |
|---|---|---|---|
| biopeat | Público | `1c21adb8a651c19771ea4ebe6ee49def9243971b` | [ESTADO.md](catalogo/biopeat/ESTADO.md) · [resumen.html](catalogo/biopeat/resumen.html) · [estado.json](catalogo/biopeat/estado.json) · [AGENTS.md](catalogo/biopeat/files/AGENTS.md) |
| Finanzas | Público | `9cb8b81621da18cfbf4a558c5cd64fb7bb1e3b47` | [ESTADO.md](catalogo/finanzas/ESTADO.md) · [resumen.html](catalogo/finanzas/resumen.html) · [estado.json](catalogo/finanzas/estado.json) · [AGENTS.md](catalogo/finanzas/files/AGENTS.md) |
| estadisticas | Público | `fb7a56a4efaeae13c9f73518518f73388ceb6a98` | [ESTADO.md](catalogo/estadisticas/ESTADO.md) · [resumen.html](catalogo/estadisticas/resumen.html) · [estado.json](catalogo/estadisticas/estado.json) · [AGENTS.md](catalogo/estadisticas/files/AGENTS.md) |

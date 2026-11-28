# PUENTE IA · PORTAL ÚNICO (Antigravity ↔ Copilot)

- **Panel y guía para Diego:** [index.html](index.html) · [GUIA_DIEGO.md](GUIA_DIEGO.md)
- **Referencia completa:** [PARA_COPILOT_LEEME.md](PARA_COPILOT_LEEME.md) · [HISTORIAL.md](HISTORIAL.md)

## INSTRUCCIONES OBLIGATORIAS PARA COPILOT (Protocolo 1.1)

1. **Si Diego continúa una tarea de Antigravity:** lee el bloque **Último traspaso / estado actual** de abajo y los archivos enlazados en `handoffs/<ID>/context/`. Usa `origin_mode: "reply_to_handoff"`.
2. **Si Diego empieza una tarea desde cero:** abre el proyecto en la tabla **Catálogo actual** (`ESTADO.md`, `estado.json`), lee obligatoriamente su `AGENTS.md` y todos los archivos reales afectados en `catalogo/<slug>/files/`. Usa el `commit` exacto de la tabla como `source_commit` y `origin_mode: "copilot_from_scratch"`.
3. **PROHIBIDO SUPONER O INVENTAR:** si algún enlace da error, no puedes leer un archivo o falta un requisito, **PARA antes de empezar** y pídele a Diego exactamente lo que te falta.
4. **Formato de entrega:** devuelve un ZIP `COPILOT_A_ANTIGRAVITY_<ID>.zip` con `HANDOFF.json` (`protocol_version` `1.1`, `task_id`, `direction: "copilot_to_antigravity"`, `origin_mode`, `project`, `repo_url`, `branch`, `source_commit`, `created_at`, `objective`, `files` con SHA-256 minúsculas), `RESPUESTA.md`, `PRUEBAS.md` y, si hay cambios, `PATCH.diff` y/o `files/` (`deleted_files` opcional). Prohibidos ejecutables binarios, scripts no declarados, `..`, rutas absolutas o secretos.

## Último traspaso / estado actual

# Resultado de importación y cierre

- **ID:** biopeat-v84-fluidez-copilot
- **Modo de origen:** `copilot_from_scratch`
- **Proyecto:** biopeat
- **Repositorio:** https://github.com/BioPeat/biopeat.git
- **Rama:** main
- **Commit de origen:** `ffc06dffd33b35e2ab67e185582e8735984e641b`
- **Commit final:** `ec2226cf72d2a734c8d932f81309082ca875bce0`
- **Estado:** `applied`
- **Registrado (UTC):** 2026-11-28T12:53:57.173601+00:00

## Resumen

Adaptadas las 5 propuestas de fluidez de Copilot (v81) a BioPeat modular v84: splash animado claro/oscuro, content-visibility ampliado, guardado diferido queueSave/flushQueuedSave, respuesta tactil/animaciones suaves y sw.js v15 sin cache en ?u=.

## Pruebas ejecutadas en Antigravity

node --check, security_check.py, smoke.py y revision visual movil claro/oscuro

## Notas

Sin incidencias adicionales.

## Catálogo actual de repositorios públicos

| Proyecto | Visibilidad | Commit actual (`source_commit`) | Enlaces directos |
|---|---|---|---|
| biopeat | Público | `ec2226cf72d2a734c8d932f81309082ca875bce0` | [ESTADO.md](catalogo/biopeat/ESTADO.md) · [resumen.html](catalogo/biopeat/resumen.html) · [estado.json](catalogo/biopeat/estado.json) · [AGENTS.md](catalogo/biopeat/files/AGENTS.md) |
| Finanzas | Público | `6b246e0353ec5c7f7432339a60a30989f5316a03` | [ESTADO.md](catalogo/finanzas/ESTADO.md) · [resumen.html](catalogo/finanzas/resumen.html) · [estado.json](catalogo/finanzas/estado.json) · [AGENTS.md](catalogo/finanzas/files/AGENTS.md) |
| estadisticas | Público | `d2b6ba9be4dec2cf0f4d5e158b78b089a8f61c80` | [ESTADO.md](catalogo/estadisticas/ESTADO.md) · [resumen.html](catalogo/estadisticas/resumen.html) · [estado.json](catalogo/estadisticas/estado.json) · [AGENTS.md](catalogo/estadisticas/files/AGENTS.md) |

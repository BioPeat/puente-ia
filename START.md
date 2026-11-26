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

- **ID:** reparto-puntos-ad1eddfd
- **Modo de origen:** `copilot_from_scratch`
- **Proyecto:** estadisticas
- **Repositorio:** https://github.com/BioPeat/estadisticas.git
- **Rama:** main
- **Commit de origen:** `0c2fc471b076516b9ca44449c20c5fb85988e2f9`
- **Commit final:** `42f6ecdfb20a067c4cdf4ee6e7b291347901ab3c`
- **Estado:** `applied`
- **Registrado (UTC):** 2026-11-24T14:25:56.051938+00:00

## Resumen

Modal Reparto de puntos ampliado con resumen, mapa de puntos y evolución individual sin tocar Minutos; SW actualizado.

## Pruebas ejecutadas en Antigravity

validate.py, worker_mock.mjs, smoke.py, updater_e2e.py

## Notas

Sin incidencias adicionales.

## Catálogo actual de repositorios públicos

| Proyecto | Visibilidad | Commit actual (`source_commit`) | Enlaces directos |
|---|---|---|---|
| biopeat | Público | `ffc06dffd33b35e2ab67e185582e8735984e641b` | [ESTADO.md](catalogo/biopeat/ESTADO.md) · [resumen.html](catalogo/biopeat/resumen.html) · [estado.json](catalogo/biopeat/estado.json) · [AGENTS.md](catalogo/biopeat/files/AGENTS.md) |
| Finanzas | Público | `9cb8b81621da18cfbf4a558c5cd64fb7bb1e3b47` | [ESTADO.md](catalogo/finanzas/ESTADO.md) · [resumen.html](catalogo/finanzas/resumen.html) · [estado.json](catalogo/finanzas/estado.json) · [AGENTS.md](catalogo/finanzas/files/AGENTS.md) |
| estadisticas | Público | `d2b6ba9be4dec2cf0f4d5e158b78b089a8f61c80` | [ESTADO.md](catalogo/estadisticas/ESTADO.md) · [resumen.html](catalogo/estadisticas/resumen.html) · [estado.json](catalogo/estadisticas/estado.json) · [AGENTS.md](catalogo/estadisticas/files/AGENTS.md) |

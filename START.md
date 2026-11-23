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

- **ID:** 20261123-prueba-inicial
- **Modo:** `reply_to_handoff`
- **Proyecto:** biopeat
- **Repositorio:** https://github.com/BioPeat/biopeat.git
- **Rama:** main
- **Commit de origen:** `1c21adb8a651c19771ea4ebe6ee49def9243971b`
- **Creado:** 2026-11-23T13:35:23.572796+00:00
- **Estado:** listo_para_copilot

## Objetivo

Traspaso de prueba inicial v1.1.0 sin modificar BioPeat

## Qué se ha hecho

Instalacion de copilot-bridge v1.1.0, catalogo sincronizado y puente inicializado.

## Qué falta

Leer PARA_COPILOT_LEEME.md y confirmar lectura desde Microsoft Copilot.

## Archivos de contexto

- [context/README.md](context/README.md) — `f4b78c8f993e0b2c171e93348809f554ea2d9d13482433beffdfeea5ae5315f2`
- [context/AGENTS.md](context/AGENTS.md) — `9b91fb1b0d76d72974b47d62cb65f185bbff430b3bba858c8fbb14599c8defe4`

## Pruebas ejecutadas y resultado

self_test.py 26/26 superadas.

## Decisiones y restricciones

No modificar codigo de biopeat, Finanzas ni estadisticas en esta prueba inicial.

## Pregunta concreta para Copilot

Confirma ID, proyecto, commit de origen y que puedes abrir los archivos del catalogo.

## Regla de entrega

Responder con `COPILOT_A_ANTIGRAVITY_20261123-prueba-inicial.zip` incluyendo `HANDOFF.json` (`protocol_version`: `1.1`, `direction`: `copilot_to_antigravity`, `origin_mode`: `reply_to_handoff`, `source_commit`: `1c21adb8a651c19771ea4ebe6ee49def9243971b`), `RESPUESTA.md`, `PRUEBAS.md` y, si hay cambios, `PATCH.diff` y `files/`.

## Catálogo actual de repositorios públicos

| Proyecto | Visibilidad | Commit actual (`source_commit`) | Enlaces directos |
|---|---|---|---|
| biopeat | Público | `1c21adb8a651c19771ea4ebe6ee49def9243971b` | [ESTADO.md](catalogo/biopeat/ESTADO.md) · [resumen.html](catalogo/biopeat/resumen.html) · [estado.json](catalogo/biopeat/estado.json) · [AGENTS.md](catalogo/biopeat/files/AGENTS.md) |
| Finanzas | Público | `9cb8b81621da18cfbf4a558c5cd64fb7bb1e3b47` | [ESTADO.md](catalogo/finanzas/ESTADO.md) · [resumen.html](catalogo/finanzas/resumen.html) · [estado.json](catalogo/finanzas/estado.json) · [AGENTS.md](catalogo/finanzas/files/AGENTS.md) |
| estadisticas | Público | `fb7a56a4efaeae13c9f73518518f73388ceb6a98` | [ESTADO.md](catalogo/estadisticas/ESTADO.md) · [resumen.html](catalogo/estadisticas/resumen.html) · [estado.json](catalogo/estadisticas/estado.json) · [AGENTS.md](catalogo/estadisticas/files/AGENTS.md) |

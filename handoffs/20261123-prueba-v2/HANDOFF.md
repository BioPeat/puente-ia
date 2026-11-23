# Traspaso a Copilot

- **ID:** 20261123-prueba-v2
- **Modo:** `reply_to_handoff`
- **Proyecto:** biopeat
- **Repositorio:** https://github.com/BioPeat/biopeat.git
- **Rama:** main
- **Commit de origen:** `1c21adb8a651c19771ea4ebe6ee49def9243971b`
- **Creado:** 2026-11-23T16:59:11.000296+00:00
- **Estado:** listo_para_copilot

## Objetivo

Traspaso de prueba v2.0.0 autocontenido sin modificar BioPeat

## Qué se ha hecho

Panel web anti-cache (index.html), PARA_COPILOT.txt y ESTADO_<app>.txt generados.

## Qué falta

Confirmar desde Microsoft Copilot la lectura del archivo PARA_COPILOT.txt (y/o ESTADO_<app>.txt) sin necesidad de abrir enlaces.

## Archivos de contexto

- [context/README.md](context/README.md) — `f4b78c8f993e0b2c171e93348809f554ea2d9d13482433beffdfeea5ae5315f2`
- [context/AGENTS.md](context/AGENTS.md) — `9b91fb1b0d76d72974b47d62cb65f185bbff430b3bba858c8fbb14599c8defe4`

## Pruebas ejecutadas y resultado

self_test.py 30/30 superadas.

## Decisiones y restricciones

No modificar codigo de biopeat, Finanzas ni estadisticas en esta prueba inicial.

## Pregunta concreta para Copilot

Confirma el ID, proyecto, commit de origen y que recibiste tanto PARA_COPILOT_LEEME.md como los archivos completos con sus SHA-256.

## Regla de entrega

Responder con `COPILOT_A_ANTIGRAVITY_20261123-prueba-v2.zip` incluyendo `HANDOFF.json` (`protocol_version`: `1.1`, `direction`: `copilot_to_antigravity`, `origin_mode`: `reply_to_handoff`, `source_commit`: `1c21adb8a651c19771ea4ebe6ee49def9243971b`), `RESPUESTA.md`, `PRUEBAS.md` y, si hay cambios, `PATCH.diff` y `files/`.

# Reglas del repositorio puente

1. Este repositorio es un buzón y catálogo público de contexto técnico; no es una app de producción.
2. Antes de hacer commit o push, ejecutar el control de seguridad (`bridge_tool.py safety` o `tools/sync_catalogo.py --safety-only`).
3. Prohibido subir secretos, `.env`, tokens, cookies, claves privadas, datos financieros reales, diarios privados, bases de datos, backups, exports o información personal.
4. Prohibido publicar rutas locales de usuario de Windows o nombres de cuenta del equipo.
5. `ULTIMO_TRASPASO.md` apunta a la última tarea o resultado, con repositorio, rama y commit exactos.
6. `CATALOGO.md` y `catalogo/` exponen exclusivamente archivos de texto públicos de los repositorios marcados como `public: true` en `catalogo_fuentes.json`.
7. No modificar código de las apps desde este repositorio.
8. Un solo agente escribe en una app a la vez; validar siempre manifiesto, `source_commit`, `PATCH.diff`, archivos completos y pruebas antes de aplicar.
9. El sistema es genérico: cualquier repo futuro se añade dinámicamente en la skill global y en `catalogo_fuentes.json`.

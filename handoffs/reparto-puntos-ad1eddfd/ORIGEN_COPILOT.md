# Tarea iniciada desde Copilot

- **ID:** reparto-puntos-ad1eddfd
- **Modo de origen:** `copilot_from_scratch`
- **Proyecto:** estadisticas
- **Repositorio:** https://github.com/BioPeat/estadisticas.git
- **Rama:** main
- **Commit base (`source_commit`):** `0c2fc471b076516b9ca44449c20c5fb85988e2f9`
- **Registrado (UTC):** 2026-11-24T14:25:56.051938+00:00

## Respuesta original de Copilot

# Reparto de puntos con las funciones de Minutos

## Objetivo
En Equipo, la ventana **Puntos · Reparto completo** incorpora los mismos bloques y gráficos que **Minutos · Carga y evolución**. La ventana de Minutos **no se modifica**.

## Qué añade la ventana Reparto completo
Se conservan el selector Totales / Por partido y las barras actuales. Debajo se añade:
1. **Resumen** (3 tarjetas, como Minutos): Partidos · Puntos equipo · Media jugadora-acta (puntos / apariciones en acta).
2. **Mapa de puntos**: tabla desplazable con Jugadora, Media (PTS/P), Cuota (% de los puntos del equipo) y P1…Pn con los puntos de cada partido coloreados por intensidad. Si no jugó ese partido: «—», nunca 0. Tocar una fila abre la ficha individual.
3. **Evolución individual**: mini gráfico de puntos por partido, media /P y cuota de temporada por jugadora.

La explicación superior añade: «La cuota compara sus puntos con los N del equipo».

## Archivos
- `app.js`: nuevas funciones `pointSeries` y `pointsHeatmap`; `openPointShareDetail` ampliada. Reutiliza `sparkline` y las clases CSS de Minutos (`minutes-heatmap`, `heat-row`, `minutes-scroll`, `minutes-evolution`, `metric-summary three`), así que **no se toca `styles.css`**. `openMinutesDetail` y `minutesHeatmap` quedan intactas.
- `sw.js`: CACHE `estadisticas-v12.3-20261124a` (fuerza la actualización en los móviles).
- `CHANGELOG.md`: nueva entrada.
- `tests/smoke.py`: comprueba la nueva ventana y que Minutos sigue igual.

No se cambian `APP_VERSION`, `?v=12.3`, los almacenes, las rutas w2, el Worker ni `assets/`.

## Aplicar
`git apply PATCH.diff` (si hay problemas de espacios: `git apply --ignore-whitespace PATCH.diff`). Los hunks usan números de línea orientativos; git localiza el contexto por desplazamiento.

## Pruebas reportadas por Copilot

# Pruebas

## Hechas en la entrega
- `git apply --check` y aplicación correcta del parche sobre los fragmentos originales de `app.js`, `sw.js`, `CHANGELOG.md` y `tests/smoke.py` (resultado idéntico al esperado).
- Ejecución en Node de la nueva `openPointShareDetail` con datos simulados (2 partidos, 3 jugadoras): totales, medias, cuotas, celdas «—» para partidos no jugados, jugadora sin acta con «—» en media y cuota, y modos Totales / Por partido.

## Pendientes en el repositorio (obligatorias según AGENTS.md)
```bash
python tools/validate.py . --allow-assets
node tests/worker_mock.mjs
ESTADISTICAS_SECOND_BACKUP='tests/fixtures/estadisticas-2026-11-16 (4).json' python tests/smoke.py
python tests/updater_e2e.py
```
`smoke.py` ahora abre Reparto completo (390 px) y comprueba: 3 tarjetas de resumen, una fila por jugadora en el mapa y en la evolución, columnas P1…Pn, cambio a Por partido, sin desbordamiento horizontal, y que Minutos sigue mostrando su tabla y evolución sin elementos de puntos.

## Verificación manual
Equipo › Reparto de puntos › «Ver jugadoras» → bajar hasta Mapa de puntos y Evolución individual; abrir también Minutos y comprobar que está igual que antes.

# puente-ia

Repositorio público de coordinación bidireccional entre **Google Antigravity** y **Microsoft Copilot** (`Protocolo Puente IA 1.1`).

## Enlaces principales (3 canales redundantes)

- **Para Copilot (primer contacto / guía completa):** [PARA_COPILOT_LEEME.md](PARA_COPILOT_LEEME.md)
- **Sentido 1 (`Antigravity -> Copilot`):**
  - GitHub: [ULTIMO_TRASPASO.md](ULTIMO_TRASPASO.md)
  - GitHub Pages: `https://biopeat.github.io/puente-ia/ultimo.html`
  - Raw: `https://raw.githubusercontent.com/BioPeat/puente-ia/main/ULTIMO_TRASPASO.md`
- **Sentido 2 (`Copilot -> Antigravity` desde cero):**
  - GitHub: [CATALOGO.md](CATALOGO.md)
  - GitHub Pages: `https://biopeat.github.io/puente-ia/catalogo.html`
  - Raw: `https://raw.githubusercontent.com/BioPeat/puente-ia/main/CATALOGO.md`
- **Historial:** [HISTORIAL.md](HISTORIAL.md)

## Cómo funciona

1. **Antigravity → Copilot:** Antigravity publica el traspaso en `handoffs/<ID>/` y actualiza `ULTIMO_TRASPASO.md` y `ultimo.html`. Copilot devuelve un ZIP compatible por descarga + PairDrop, y Antigravity valida, aplica, prueba y registra `RESULTADO.md`.
2. **Copilot → Antigravity desde cero:** Copilot lee `CATALOGO.md` (o `catalogo/<slug>/ESTADO.md` y `catalogo/<slug>/files/...`), verifica el `source_commit` real, nunca supone código que no ha visto y devuelve un ZIP `COPILOT_A_ANTIGRAVITY_<ID>.zip` con `origin_mode: "copilot_from_scratch"`. Antigravity lo valida, lo aplica, ejecuta pruebas reales y actualiza el puente.

## Seguridad

Repositorio público. Solo admite código que ya sea público y metadatos técnicos no sensibles.

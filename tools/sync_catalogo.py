#!/usr/bin/env python3
"""Sincronizador público del catálogo de repos para GitHub Actions / CLI. Solo stdlib."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

sys.dont_write_bytecode = True

PROTOCOL = "1.1"
MAX_CONTEXT_FILE = 2 * 1024 * 1024
FORBIDDEN_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "secrets.json"}
FORBIDDEN_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".sqlite", ".sqlite3", ".db"}
SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[ \t]*\r?\n[A-Za-z0-9+/=\r\n]{32,}")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("AWS Access Key ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("Windows user path", re.compile(r"[A-Za-z]:[\\/]Users[\\/][^\\/\s\"'`<>|]+", re.IGNORECASE)),
]
REPO_URL_RE = re.compile(r"^https://github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?/?$", re.IGNORECASE)
CATALOG_SKIP_EXACT = {".agents/REGISTRO_CONFIG_ANTIGRAVITY.md"}
CATALOG_SKIP_PARTS = {".git", "node_modules", "__pycache__"}
CATALOG_TEXT_SUFFIXES = {
    ".html", ".htm", ".js", ".mjs", ".cjs", ".css", ".md", ".txt", ".json",
    ".py", ".sql", ".yml", ".yaml", ".svg", ".xml", ".toml", ".ini", ".ts", ".tsx", ".jsx",
}
CATALOG_TEXT_NAMES = {
    "AGENTS.md", "GEMINI.md", "README.md", ".gitignore", ".nojekyll", "LICENSE", "Makefile",
}


class SyncError(Exception):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def text_lf_info(path: Path) -> tuple[str, str, str]:
    raw_bytes = path.read_bytes()
    eol = "crlf" if b"\r\n" in raw_bytes else "lf"
    lf_bytes = raw_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    sha_lf = hashlib.sha256(lf_bytes).hexdigest()
    text_lf = lf_bytes.decode("utf-8")
    return text_lf, sha_lf, eol


def safe_rel(raw: str) -> PurePosixPath:
    cleaned = raw.replace("\\", "/").strip("/")
    rel = PurePosixPath(cleaned)
    if not cleaned or rel.is_absolute() or ".." in rel.parts or any(":" in p or "\x00" in p for p in rel.parts):
        raise SyncError(f"Ruta insegura: {raw}")
    return rel


def forbidden_file(path: Path) -> str | None:
    low = path.name.lower()
    if low in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
        return "nombre o extensión sensible"
    if low.startswith(".env.") or "backup" in low or "extracto" in low:
        return "nombre potencialmente privado"
    return None


def scan_text(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    return [lbl for lbl, rx in SECRET_PATTERNS if rx.search(text)]


def safety_scan(root: Path) -> list[str]:
    errors: list[str] = []
    for p in root.rglob("*"):
        if ".git" in p.parts or not p.is_file():
            continue
        rel = p.relative_to(root)
        if p.is_symlink():
            errors.append(f"{rel}: enlace simbólico no permitido")
            continue
        reason = forbidden_file(p)
        if reason:
            errors.append(f"{rel}: {reason}")
        if p.stat().st_size > MAX_CONTEXT_FILE and ("handoffs" in p.parts or "catalogo" in p.parts):
            errors.append(f"{rel}: archivo de contexto mayor de {MAX_CONTEXT_FILE} bytes")
        for finding in scan_text(p):
            errors.append(f"{rel}: posible {finding}")
    return errors


def is_catalog_text(path: Path) -> bool:
    low = path.name.lower()
    if low.endswith((".min.js", ".min.css", ".map")):
        return False
    return path.name in CATALOG_TEXT_NAMES or path.suffix.lower() in CATALOG_TEXT_SUFFIXES


def render_html_doc(title: str, md_body: str, links: list[tuple[str, str]]) -> str:
    nav = " · ".join(f'<a href="{html.escape(h)}">{html.escape(l)}</a>' for l, h in links)
    return (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<meta name='robots' content='noindex,nofollow'>"
        f"<title>{html.escape(title)}</title>"
        "<style>body{font:15px/1.6 system-ui,sans-serif;max-width:940px;margin:32px auto;padding:0 20px;background:#111318;color:#e7e9ee}"
        "a{color:#7cc4ff}pre{white-space:pre-wrap;word-break:break-word;background:#191d24;padding:18px;border-radius:10px;border:1px solid #2b3240}"
        ".warn{color:#f5b971}</style></head><body>"
        f"<h1>Puente IA · {html.escape(title)}</h1><nav style='margin-bottom:16px'>{nav}</nav>"
        "<p class='warn'>Contenido público técnico. Prohibido incluir secretos o datos privados.</p>"
        f"<pre>{html.escape(md_body)}</pre></body></html>\n"
    )


def refresh_portal(bridge: Path) -> None:
    state: dict = {}
    state_file = bridge / "estado.json"
    if state_file.is_file():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}

    latest_id = state.get("latest_task_id")
    latest_detail = ""
    if latest_id:
        for cand in ("HANDOFF.md", "RESULTADO.md", "ORIGEN_COPILOT.md"):
            p = bridge / "handoffs" / str(latest_id) / cand
            if p.is_file():
                latest_detail = p.read_text(encoding="utf-8", errors="replace").strip()
                break
    if not latest_detail and (bridge / "ULTIMO_TRASPASO.md").is_file():
        latest_detail = (bridge / "ULTIMO_TRASPASO.md").read_text(encoding="utf-8", errors="replace").strip()
    if not latest_detail:
        latest_detail = "Todavía no hay ningún traspaso registrado."

    cat_projects: list[dict] = []
    cat_file = bridge / "catalogo.json"
    if cat_file.is_file():
        try:
            cat_projects = json.loads(cat_file.read_text(encoding="utf-8")).get("projects", [])
        except json.JSONDecodeError:
            cat_projects = []

    cat_rows_md = []
    cat_rows_html = []
    for e in cat_projects:
        name = str(e.get("name", ""))
        slug = str(e.get("slug", name.lower()))
        if not e.get("public"):
            cat_rows_md.append(f"| {name} | Privado | - | No copiado (usar PairDrop) |")
            cat_rows_html.append(
                f"<tr><td>{html.escape(name)}</td><td>Privado</td><td><code>-</code></td><td>No copiado (usar PairDrop)</td></tr>"
            )
        else:
            commit = str(e.get("commit", ""))
            short_c = commit[:10]
            cat_rows_md.append(
                f"| {name} | Público | `{commit}` | "
                f"[ESTADO.md](catalogo/{slug}/ESTADO.md) · [resumen.html](catalogo/{slug}/resumen.html) · "
                f"[estado.json](catalogo/{slug}/estado.json) · [AGENTS.md](catalogo/{slug}/files/AGENTS.md) |"
            )
            cat_rows_html.append(
                f"<tr><td><strong>{html.escape(name)}</strong></td><td>Público</td>"
                f"<td><code title='{html.escape(commit)}'>{html.escape(short_c)}</code></td>"
                f"<td><a href='catalogo/{html.escape(slug)}/resumen.html'>resumen</a> · "
                f"<a href='catalogo/{html.escape(slug)}/ESTADO.md'>ESTADO.md</a> · "
                f"<a href='catalogo/{html.escape(slug)}/estado.json'>estado.json</a> · "
                f"<a href='catalogo/{html.escape(slug)}/files/AGENTS.md'>AGENTS.md</a></td></tr>"
            )

    cat_table_md = (
        "| Proyecto | Visibilidad | Commit actual (`source_commit`) | Enlaces directos |\n|---|---|---|---|\n"
        + ("\n".join(cat_rows_md) if cat_rows_md else "| (sin proyectos) | - | - | - |")
    )

    instructions_md = (
        "## INSTRUCCIONES OBLIGATORIAS PARA COPILOT (Protocolo 1.1)\n\n"
        "1. **Si Diego continúa una tarea de Antigravity:** lee el bloque **Último traspaso / estado actual** de abajo y los archivos enlazados en `handoffs/<ID>/context/`. Usa `origin_mode: \"reply_to_handoff\"`.\n"
        "2. **Si Diego empieza una tarea desde cero:** abre el proyecto en la tabla **Catálogo actual** (`ESTADO.md`, `estado.json`), lee obligatoriamente su `AGENTS.md` y todos los archivos reales afectados en `catalogo/<slug>/files/`. Usa el `commit` exacto de la tabla como `source_commit` y `origin_mode: \"copilot_from_scratch\"`.\n"
        "3. **PROHIBIDO SUPONER O INVENTAR:** si algún enlace da error, no puedes leer un archivo o falta un requisito, **PARA antes de empezar** y pídele a Diego exactamente lo que te falta.\n"
        "4. **Formato de entrega:** devuelve un ZIP `COPILOT_A_ANTIGRAVITY_<ID>.zip` con `HANDOFF.json` (`protocol_version` `1.1`, `task_id`, `direction: \"copilot_to_antigravity\"`, `origin_mode`, `project`, `repo_url`, `branch`, `source_commit`, `created_at`, `objective`, `files` con SHA-256 minúsculas), `RESPUESTA.md`, `PRUEBAS.md` y, si hay cambios, `PATCH.diff` y/o `files/` (`deleted_files` opcional). Prohibidos ejecutables binarios, scripts no declarados, `..`, rutas absolutas o secretos.\n"
    )

    start_md = (
        "# PUENTE IA · PORTAL ÚNICO (Antigravity ↔ Copilot)\n\n"
        "- **Guía rápida para Diego:** [guia.html](guia.html) · [GUIA_DIEGO.md](GUIA_DIEGO.md)\n"
        "- **Referencia completa:** [PARA_COPILOT_LEEME.md](PARA_COPILOT_LEEME.md) · [HISTORIAL.md](HISTORIAL.md)\n\n"
        f"{instructions_md}\n"
        "## Último traspaso / estado actual\n\n"
        f"{latest_detail}\n\n"
        "## Catálogo actual de repositorios públicos\n\n"
        f"{cat_table_md}\n"
    )
    (bridge / "START.md").write_text(start_md, encoding="utf-8")

    index_path = bridge / "index.html"
    if index_path.is_file() and "<!-- PUENTE_IA_PANEL -->" in index_path.read_text(encoding="utf-8", errors="ignore"):
        return

    cat_table_html = (
        "<table><thead><tr><th>Proyecto</th><th>Visibilidad</th><th>Commit actual</th><th>Enlaces</th></tr></thead><tbody>"
        + ("".join(cat_rows_html) if cat_rows_html else "<tr><td colspan='4'>Sin proyectos sincronizados todavía.</td></tr>")
        + "</tbody></table>"
    )
    status_badge = html.escape(str(state.get("status", "empty")))
    latest_id_esc = html.escape(str(latest_id or "ninguno"))
    index_html = (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<meta name='robots' content='noindex,nofollow'>"
        "<title>Puente IA · Portal único Copilot ↔ Antigravity</title>"
        "<style>:root{color-scheme:dark light}body{font:15px/1.6 system-ui,sans-serif;max-width:960px;margin:28px auto;padding:0 18px;background:#111318;color:#e7e9ee}"
        "a{color:#7cc4ff}.card{background:#191d24;border:1px solid #2b3240;border-radius:12px;padding:16px 18px;margin:14px 0}"
        "pre{white-space:pre-wrap;word-break:break-word;background:#13161d;padding:14px;border-radius:8px;border:1px solid #262c38;margin:8px 0 0}"
        "table{border-collapse:collapse;width:100%;margin-top:8px}th,td{border:1px solid #2b3240;padding:8px 10px;text-align:left}"
        ".warn{color:#f5b971}.nav a{margin-right:12px;font-weight:600}.pill{display:inline-block;padding:2px 8px;border-radius:999px;background:#232a36;font-size:13px}</style></head><body>"
        "<h1>Puente IA · Portal único (v1.2)</h1>"
        "<nav class='nav'>"
        "<a href='guia.html'>Guía visual para Diego</a>"
        "<a href='START.md'>START.md (Markdown)</a>"
        "<a href='ultimo.html'>Último traspaso</a>"
        "<a href='catalogo.html'>Catálogo completo</a>"
        "<a href='PARA_COPILOT_LEEME.md'>PARA_COPILOT_LEEME.md</a>"
        "</nav>"
        "<p class='warn'>Contenido técnico público. Prohibido incluir secretos, rutas locales o datos privados.</p>"
        "<div class='card'><h2>Instrucciones para Copilot (Protocolo 1.1)</h2>"
        f"<pre>{html.escape(instructions_md)}</pre></div>"
        f"<div class='card'><h2>Último traspaso / estado <span class='pill'>{latest_id_esc} · {status_badge}</span></h2>"
        f"<pre>{html.escape(latest_detail)}</pre></div>"
        f"<div class='card'><h2>Catálogo actual de apps públicas</h2>{cat_table_html}</div>"
        "</body></html>\n"
    )
    (bridge / "index.html").write_text(index_html, encoding="utf-8")


def run_sync(bridge: Path) -> int:
    sources_path = bridge / "catalogo_fuentes.json"
    if not sources_path.is_file():
        raise SyncError("Falta catalogo_fuentes.json en la raíz del puente.")
    sources_doc = json.loads(sources_path.read_text(encoding="utf-8"))
    bridge_repo_url = sources_doc.get("bridge_repo_url", "https://github.com/BioPeat/puente-ia.git").rstrip("/")
    m_bridge = REPO_URL_RE.match(bridge_repo_url)
    if not m_bridge:
        raise SyncError(f"bridge_repo_url inválida: {bridge_repo_url}")
    b_owner, b_repo = m_bridge.group(1), m_bridge.group(2)
    pages_root = sources_doc.get("pages_root_url", f"https://{b_owner.lower()}.github.io/{b_repo}/").rstrip("/") + "/"
    raw_root = f"https://raw.githubusercontent.com/{b_owner}/{b_repo}/main/"

    existing_cat = {}
    if (bridge / "catalogo.json").is_file():
        for e in json.loads((bridge / "catalogo.json").read_text(encoding="utf-8")).get("projects", []):
            existing_cat[e["slug"]] = e.get("commit")

    now = datetime.now(timezone.utc)
    changed_any = False
    tmp = tempfile.TemporaryDirectory(prefix="puente-ci-sync-")
    try:
        tmp_path = Path(tmp.name)
        entries = []
        for src_info in sources_doc.get("sources", []):
            name = src_info["name"]
            slug = src_info["slug"]
            repo_url = src_info["repo_url"].rstrip("/")
            pages_url = src_info.get("pages_url", "")
            branch = src_info.get("branch", "main")
            is_public = bool(src_info.get("public", False))
            if not is_public:
                entries.append({
                    "name": name, "slug": slug, "repo_url": repo_url, "pages_url": pages_url,
                    "public": False, "status": "private_not_mirrored", "synced_at": now.isoformat(),
                })
                continue

            clone_dir = tmp_path / slug
            cp = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, str(clone_dir)],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            if cp.returncode != 0:
                raise SyncError(f"No se pudo clonar {repo_url}: {cp.stderr.strip()}")
            commit = subprocess.check_output(["git", "-C", str(clone_dir), "rev-parse", "HEAD"], text=True).strip()
            if existing_cat.get(slug) == commit and (bridge / "catalogo" / slug / "estado.json").is_file():
                entries.append(json.loads((bridge / "catalogo" / slug / "estado.json").read_text(encoding="utf-8")))
                continue

            changed_any = True
            raw_files = subprocess.check_output(["git", "-C", str(clone_dir), "ls-files", "-z"])
            tracked = [x.decode("utf-8", errors="surrogateescape") for x in raw_files.split(b"\x00") if x]

            stage_dir = tmp_path / f"stage-{slug}"
            stage_files = stage_dir / "files"
            stage_files.mkdir(parents=True, exist_ok=True)
            files_out = []
            omitted_out = []
            for rel_raw in tracked:
                rel = safe_rel(rel_raw)
                rel_posix = rel.as_posix()
                src = (clone_dir / Path(*rel.parts)).resolve()
                if rel_posix in CATALOG_SKIP_EXACT or ".agents/backups" in rel_posix or any(p in CATALOG_SKIP_PARTS for p in rel.parts):
                    omitted_out.append({"path": rel_posix, "reason": "metadato o carpeta interna excluida"})
                    continue
                if not src.is_file() or src.is_symlink():
                    omitted_out.append({"path": rel_posix, "reason": "no es archivo normal"})
                    continue
                reason = forbidden_file(src)
                if reason:
                    omitted_out.append({"path": rel_posix, "reason": reason})
                    continue
                if not is_catalog_text(src):
                    omitted_out.append({"path": rel_posix, "reason": "binario o minificado", "size": src.stat().st_size})
                    continue
                sz = src.stat().st_size
                if sz > MAX_CONTEXT_FILE:
                    omitted_out.append({"path": rel_posix, "reason": f"excede {MAX_CONTEXT_FILE} bytes", "size": sz})
                    continue
                findings = scan_text(src)
                if findings:
                    raise SyncError(f"Posible secreto en {name}/{rel_posix}: {', '.join(findings)}")
                dst = stage_files / Path(*rel.parts)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                files_out.append({"path": rel_posix, "size": sz, "sha256": sha256(dst)})

            entry = {
                "name": name, "slug": slug, "repo_url": repo_url, "pages_url": pages_url,
                "branch": branch, "commit": commit, "dirty_local": False, "public": True,
                "status": "synced", "synced_at": now.isoformat(),
                "file_count": len(files_out), "omitted_count": len(omitted_out),
                "estado_txt_path": f"catalogo/{slug}/ESTADO_{slug}.txt",
                "files": files_out, "omitted": omitted_out,
                "urls": {
                    "pages_summary": f"{pages_root}catalogo/{slug}/resumen.html",
                    "pages_state_json": f"{pages_root}catalogo/{slug}/estado.json",
                    "pages_estado_txt": f"{pages_root}catalogo/{slug}/ESTADO_{slug}.txt",
                    "raw_state_md": f"{raw_root}catalogo/{slug}/ESTADO.md",
                    "raw_state_json": f"{raw_root}catalogo/{slug}/estado.json",
                    "raw_estado_txt": f"{raw_root}catalogo/{slug}/ESTADO_{slug}.txt",
                    "raw_files_prefix": f"{raw_root}catalogo/{slug}/files/",
                    "pages_files_prefix": f"{pages_root}catalogo/{slug}/files/",
                },
            }
            (stage_dir / "estado.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            estado_txt_lines = [
                f"PUENTE IA · ESTADO AUTOCONTENIDO DE {name.upper()} ({slug})",
                "=" * 70,
                f"PROYECTO: {name} ({slug})",
                f"REPOSITORIO: {repo_url}",
                f"APP PUBLICADA: {pages_url or 'N/A'}",
                f"RAMA: {branch}",
                f"COMMIT ACTUAL (source_commit): {commit}",
                f"SINCRONIZADO UTC: {now.isoformat()}",
                f"PROTOCOLO DE VUELTA: {PROTOCOL}",
                "",
                "INDICE COMPLETO DE ARCHIVOS PUBLICOS:",
                *[f"- {f['path']} | {f['size']} bytes | sha256: {f['sha256']}" for f in files_out],
                "",
                "ARCHIVOS OMITIDOS (binarios, minificados o >2 MB):",
                *([f"- {o['path']} ({o['reason']})" for o in omitted_out] or ["- Ninguno"]),
                "",
                "REGLA OBLIGATORIA ANTI-SUPOSICIONES:",
                "- Nunca inventes el contenido de un archivo que no esté completo aquí.",
                f"- Si necesitas leer archivos concretos de código de {name}, PARA antes de programar y pídeselos a Diego (puede empaquetarlos en 1 clic desde el panel como ARCHIVOS_{slug}.txt).",
                "",
                "DOCUMENTACION CLAVE COMPLETA:",
            ]
            key_docs_all = [
                f for f in files_out
                if f["path"] in {"AGENTS.md", "README.md", "GEMINI.md"}
                or f["path"].startswith(("CONTEXTO_", "MAPA_", "PROYECTO_"))
            ]
            if not key_docs_all:
                estado_txt_lines.append("- Ningún documento clave detectado.")
            else:
                for kd in key_docs_all:
                    if kd["size"] > 80 * 1024:
                        estado_txt_lines.append(
                            f"- {kd['path']} ({kd['size']} bytes, omitido por tamaño >80 KB; pídelo a Diego desde el panel si lo necesitas)"
                        )
                        continue
                    kd_path = stage_files / Path(*PurePosixPath(kd["path"]).parts)
                    try:
                        kd_lf, kd_sha_lf, kd_eol = text_lf_info(kd_path)
                    except UnicodeDecodeError:
                        kd_lf = kd_path.read_text(encoding="utf-8", errors="replace")
                        kd_sha_lf = hashlib.sha256(kd_lf.replace("\r\n", "\n").encode("utf-8")).hexdigest()
                        kd_eol = "lf"
                    estado_txt_lines.append(
                        f"===== FILE: {kd['path']} | sha256: {kd['sha256']} | sha256_lf: {kd_sha_lf} | eol: {kd_eol} =====\n"
                        f"{kd_lf.rstrip()}\n"
                        f"===== END FILE: {kd['path']} ====="
                    )
            estado_txt_lines.extend([
                "",
                "INSTRUCCIONES DEL ZIP DE VUELTA (DESDE CERO):",
                f"- Entrega un ZIP llamado: COPILOT_A_ANTIGRAVITY_YYYYMMDD-HHMMSS-{slug}-<6hex>.zip",
                "- Incluye HANDOFF.json con:",
                f'  - protocol_version: "{PROTOCOL}", direction: "copilot_to_antigravity", origin_mode: "copilot_from_scratch"',
                f'  - project: "{name}", repo_url: "{repo_url}", branch: "{branch}", source_commit: "{commit}"',
                '  - task_id único (>=8 chars), created_at, objective, files (con sha256 en minúsculas)',
                "- Incluye RESPUESTA.md, PRUEBAS.md y, si hay cambios, PATCH.diff y/o files/ (deleted_files opcional).",
                "- PROHIBIDO: ejecutables binarios, scripts no declarados, rutas .. o absolutas, secretos o rutas locales.",
            ])
            (stage_dir / f"ESTADO_{slug}.txt").write_text("\n".join(estado_txt_lines) + "\n", encoding="utf-8", newline="\n")
            file_rows = "\n".join(f"| [{f['path']}](files/{f['path']}) | {f['size']} | `{f['sha256'][:12]}` |" for f in files_out)
            omit_rows = "\n".join(f"- `{o['path']}` ({o['reason']})" for o in omitted_out) or "- Ninguno"
            key_docs = [f["path"] for f in files_out if f["path"] in {"AGENTS.md", "README.md"} or f["path"].startswith(("CONTEXTO_", "MAPA_"))]
            key_links = "\n".join(f"- [{k}](files/{k})" for k in key_docs) or "- Ninguno"
            estado_md = (
                f"# Estado actual de {name}\n\n"
                f"- **Proyecto:** {name} (`{slug}`)\n"
                f"- **Repositorio:** {repo_url}\n"
                f"- **App publicada:** {pages_url or 'N/A'}\n"
                f"- **Rama:** `{branch}`\n"
                f"- **Commit actual (`source_commit`):** `{commit}`\n"
                f"- **Sincronizado (UTC):** {now.isoformat()}\n"
                f"- **Archivos de texto legibles incluidos:** {len(files_out)}\n\n"
                f"## Lectura rápida recomendada (para empezar desde cero en Copilot)\n\n{key_links}\n\n"
                f"## Todos los archivos sincronizados\n\n"
                f"| Archivo | Bytes | SHA-256 |\n|---|---:|---|\n{file_rows}\n\n"
                f"## Archivos omitidos (binarios, minificados o >2 MB)\n\n{omit_rows}\n"
            )
            (stage_dir / "ESTADO.md").write_text(estado_md, encoding="utf-8")
            (stage_dir / "resumen.html").write_text(
                render_html_doc(
                    f"Catálogo · {name}",
                    estado_md,
                    [("Catálogo general", "../../catalogo.html"), ("Último traspaso", "../../ultimo.html"), ("estado.json", "estado.json")],
                ),
                encoding="utf-8",
            )
            proj_cat = bridge / "catalogo" / slug
            if proj_cat.exists():
                shutil.rmtree(proj_cat)
            shutil.copytree(stage_dir, proj_cat)
            entries.append(entry)

        if not changed_any and (bridge / "CATALOGO.md").is_file():
            print("Catálogo sin cambios de commit.")
        else:
            cat_doc = {
                "protocol_version": PROTOCOL,
                "updated_at": now.isoformat(),
                "projects": [{k: v for k, v in e.items() if k not in {"files", "omitted"}} for e in entries],
            }
            (bridge / "catalogo.json").write_text(json.dumps(cat_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            rows = []
            for e in entries:
                if not e.get("public"):
                    rows.append(f"| {e['name']} | Privado | - | - | No copiado (usar PairDrop) |")
                else:
                    rows.append(
                        f"| {e['name']} | Público | `{e['commit'][:10]}` | {e['file_count']} | "
                        f"[ESTADO.md](catalogo/{e['slug']}/ESTADO.md) · [resumen.html](catalogo/{e['slug']}/resumen.html) · [estado.json](catalogo/{e['slug']}/estado.json) |"
                    )
            cat_md = (
                f"# Catálogo actual de repositorios públicos\n\n"
                f"Actualizado (UTC): `{now.isoformat()}`\n\n"
                f"Usa este catálogo cuando pidas una tarea a Copilot **desde cero** (sin traspaso previo de Antigravity).\n\n"
                f"| Proyecto | Visibilidad | Commit actual | Archivos | Enlaces |\n|---|---|---|---:|---|\n"
                + "\n".join(rows)
                + "\n\n## Regla para Copilot\n\n"
                + "Antes de proponer o devolver cambios, lee `AGENTS.md` y los archivos reales necesarios en `catalogo/<slug>/files/` "
                + "y usa el `commit` exacto indicado arriba como `source_commit`. Si algún enlace falla o falta un archivo, **para y pídeselo a Diego**.\n"
            )
            (bridge / "CATALOGO.md").write_text(cat_md, encoding="utf-8")
            (bridge / "catalogo.html").write_text(
                render_html_doc("Catálogo de repositorios", cat_md, [("Último traspaso", "ultimo.html"), ("Inicio", "index.html"), ("catalogo.json", "catalogo.json")]),
                encoding="utf-8",
            )
            refresh_portal(bridge)
            print("Catálogo actualizado.")

        errors = safety_scan(bridge)
        if errors:
            raise SyncError("Control de seguridad fallido:\n- " + "\n- ".join(errors))
        print("Safety check OK.")
        return 0
    finally:
        tmp.cleanup()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bridge", default=".")
    ap.add_argument("--safety-only", action="store_true")
    args = ap.parse_args()
    bridge = Path(args.bridge).resolve()
    try:
        if args.safety_only:
            errs = safety_scan(bridge)
            if errs:
                raise SyncError("\n".join(errs))
            print("OK: sin coincidencias sensibles")
            return 0
        return run_sync(bridge)
    except (SyncError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

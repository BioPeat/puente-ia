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
                "files": files_out, "omitted": omitted_out,
                "urls": {
                    "pages_summary": f"{pages_root}catalogo/{slug}/resumen.html",
                    "pages_state_json": f"{pages_root}catalogo/{slug}/estado.json",
                    "raw_state_md": f"{raw_root}catalogo/{slug}/ESTADO.md",
                    "raw_state_json": f"{raw_root}catalogo/{slug}/estado.json",
                    "raw_files_prefix": f"{raw_root}catalogo/{slug}/files/",
                    "pages_files_prefix": f"{pages_root}catalogo/{slug}/files/",
                },
            }
            (stage_dir / "estado.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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

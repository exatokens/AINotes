"""Index the practical lab codebase and docs into Qdrant.

This keeps lecture material and lab implementation patterns separate. The chat
retrieval pipeline can then surface the right kind of material depending on the
user's question: concepts from lecture sources, and implementation patterns from
labs.

Current scope: README + markdown docs + selected Python source files in
/sandbox/rag-labs.
"""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

import requests

from app import config
from app.rag import embed

LABS_ROOT = config.LABS_ROOT
IGNORED_DIRS = {".git", ".venv", "__pycache__", "dist", ".pytest_cache", "node_modules", ".mypy_cache", ".ruff_cache"}
IGNORED_FILES = {".DS_Store", "uv.lock"}
TARGET_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".toml", ".txt"}


def infer_lab_week(path: Path):
    """Infer a week number from a lab path or filename when possible."""
    text = path.as_posix().lower()
    m = re.search(r"week[_ -](\d+)", text)
    if m:
        return int(m.group(1))
    if "week6" in text or "week_6" in text:
        return 6
    if "week7" in text or "week_7" in text:
        return 7
    if "week8" in text or "week_8" in text:
        return 8
    if "week9" in text or "week_9" in text:
        return 9
    if "week10" in text or "week_10" in text:
        return 10
    if "week11" in text or "week_11" in text:
        return 11
    return 0


def normalize_text(text: str) -> str:
    """Keep prose readable while dropping obvious noise from code dumps."""
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"# .*\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def gather_lab_points():
    """Collect curated chunks from the lab repo."""
    points = []
    if not LABS_ROOT.exists():
        raise FileNotFoundError(f"Lab root not found: {LABS_ROOT}")

    for path in sorted(LABS_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.name in IGNORED_FILES or any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TARGET_SUFFIXES:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        clean = normalize_text(text)
        if not clean:
            continue

        week = infer_lab_week(path)
        label = path.relative_to(LABS_ROOT).as_posix()
        kind = "lab"
        if path.suffix.lower() in {".py"}:
            kind = "implementation"
        elif path.name.lower() == "readme.md":
            kind = "lab-guide"

        title = path.name
        if path.name.lower() == "readme.md":
            title = path.parent.name or "Lab"

        for start in range(0, len(clean), 1600):
            chunk = clean[start : start + 1600].strip()
            if len(chunk) < 80:
                continue
            points.append(
                {
                    "payload": {
                        "kind": kind,
                        "week": week,
                        "title": title,
                        "section": label,
                        "path": label,
                        "text": chunk,
                    },
                    "_embed": f"{title} — {label}. {chunk}",
                }
            )
    return points


def main():
    q = config.QDRANT_URL
    requests.delete(f"{q}/collections/{config.COLLECTION_LABS}", timeout=30)
    r = requests.put(
        f"{q}/collections/{config.COLLECTION_LABS}",
        json={"vectors": {"size": config.EMBED_DIM, "distance": "Cosine"}},
        timeout=30,
    )
    r.raise_for_status()

    points = gather_lab_points()
    print(f"{len(points)} lab chunks; embedding…")
    for i in range(0, len(points), 32):
        batch = points[i : i + 32]
        vecs = embed([p.pop("_embed") for p in batch])
        payloads = [{"id": str(uuid.uuid4()), "vector": v, "payload": p["payload"]} for p, v in zip(batch, vecs)]
        r = requests.put(
            f"{q}/collections/{config.COLLECTION_LABS}/points?wait=true",
            json={"points": payloads},
            timeout=60,
        )
        r.raise_for_status()
        print(f"  upserted {min(i + 32, len(points))}/{len(points)}")
    print("done.")


if __name__ == "__main__":
    main()

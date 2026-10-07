"""Offline integrity checks for the research package, not a fact-checking engine."""

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
ids = set()
count = 0
for path in (ROOT / "docs/research/central-bank/evidence.json", ROOT / "docs/research/bsv-evidence.json"):
    body = json.loads(path.read_text())
    assert body["schema_version"] == "1.0", path
    assert body["retrieved"] == "2026-10-07", path
    for source in body["sources"]:
        assert source["id"] not in ids, source["id"]
        ids.add(source["id"])
        for field in ("title", "publisher", "retrieved", "url", "access", "limits", "source_type"):
            assert source.get(field), (path, source["id"], field)
        assert urlparse(source["url"]).scheme == "https", source["id"]
        assert source.get("claims"), source["id"]
        count += 1

links_checked = 0
for path in ROOT.rglob("*.md"):
    if ".git" in path.parts:
        continue
    text = path.read_text()
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if "://" in link or link.startswith(("#", "mailto:")):
            continue
        target = (path.parent / unquote(link.split("#")[0])).resolve()
        assert target.is_relative_to(ROOT), (path, link)
        assert target.exists(), (path, link)
        links_checked += 1

assert count >= 28, count
print(f"Validated {count} unique source entries and {links_checked} local links.")

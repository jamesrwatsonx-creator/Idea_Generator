"""Validate cross-references and prompt coverage without dependencies or network."""

import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from idea_engine.core import compile_prompt, modes, sources


def validate():
    methods, registry = modes(), sources()
    assert len(methods) == 10, "Exactly ten discovery methods must remain available"
    ids = [s["id"] for s in registry]
    assert len(ids) == len(set(ids)), "Duplicate source IDs"
    assert len({m["id"] for m in methods}) == 10, "Duplicate mode IDs"
    for method in methods:
        prompt = compile_prompt(method["id"], "Example task" if method["requires_seed"] else "")
        assert "abandon condition" in prompt and "Kill log" in prompt
        assert len(method["questions"]) >= 3
    for source in registry:
        assert source["fallback_id"] in ids, f"Missing fallback: {source['id']}"
        assert source["fallback_id"] != source["id"]
        assert source["layer"] in ("market", "structural", "capability", "acquisition")
        assert source["purpose"] and source["limitations"] and source["checked_on"]
        assert urlsplit(source["url"]).scheme == "https"
    for path in ROOT.rglob("*.json"):
        if "runs" not in path.relative_to(ROOT).parts:
            json.loads(path.read_text(encoding="utf-8"))
    print(f"Validated {len(methods)} modes, {len(registry)} source records and JSON files")


if __name__ == "__main__":
    validate()

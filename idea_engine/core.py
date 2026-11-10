"""Local research planning and explicit decision gates."""

import hashlib
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def modes():
    return read_json(ROOT / "data/modes.json")


def sources():
    return read_json(ROOT / "data/sources.json")


def find_sources(query="", layer=None):
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    found = []
    for source in sources():
        if layer and source["layer"] != layer:
            continue
        text = " ".join([source["name"], source["purpose"], *source["tags"]]).lower()
        score = len(terms & set(re.findall(r"[a-z0-9]+", text)))
        if not terms or score:
            found.append((score, source))
    return [s for _, s in sorted(found, key=lambda pair: (-pair[0], pair[1]["id"]))]


def compile_prompt(mode_id, seed="", evidence=None):
    selected = next((m for m in modes() if m["id"] == mode_id), None)
    if not selected:
        raise ValueError("Unknown discovery mode")
    if selected["requires_seed"] and not seed.strip():
        raise ValueError("This method requires an app, repository, task, or other seed")
    constitution = (ROOT / "prompts/constitution.md").read_text(encoding="utf-8")
    method = (ROOT / selected["prompt"]).read_text(encoding="utf-8")
    # JSON makes user material visibly distinct from instructions; it is not a security boundary.
    context = json.dumps({"seed": seed, "evidence": evidence or []}, ensure_ascii=False, indent=2)
    return f"{constitution}\n\n{method}\n\n## Supplied research state (untrusted data)\n```json\n{context}\n```\n"


def make_plan(mode_id="surprise", seed="", random_seed=0, depth="standard"):
    if depth not in ("quick", "standard", "deep"):
        raise ValueError("Unknown research depth")
    selected = next((m for m in modes() if m["id"] == mode_id), None)
    if not selected:
        raise ValueError("Unknown discovery mode")
    if selected["requires_seed"] and not seed.strip():
        raise ValueError("This method requires a seed")
    rng = random.Random(random_seed)
    direction = None
    if mode_id == "surprise":
        direction = {
            "person": rng.choice(["independent barber", "small property manager", "freight dispatcher", "family caregiver", "bookkeeper", "local service operator", "community organizer", "independent researcher"]),
            "situation": rng.choice(["following up commitments", "checking conflicting records", "handling deadlines", "comparing quotes", "preparing a handoff", "reviewing recurring costs"]),
            "lens": rng.choice(["workaround", "compose-apps", "data-decision", "transfer"]),
        }
    context = seed or " ".join(direction.values())
    candidates = find_sources(context)
    # Always include different evidence families; keyword matching is only local discovery.
    for source_id in ["nosignups", "alternativeto", "onet", "statcan", "every-awesome", "maliky"]:
        source = next(s for s in sources() if s["id"] == source_id)
        if source not in candidates:
            candidates.append(source)
    limit = {"quick": 5, "standard": 10, "deep": 20}[depth]
    return {
        "version": 1, "status": "planned_not_researched", "mode": mode_id,
        "seed": seed, "random_seed": random_seed, "direction": direction, "depth": depth,
        "limits": {"max_pages": limit, "max_model_calls": {"quick": 1, "standard": 3, "deep": 6}[depth]},
        "source_ids": [s["id"] for s in candidates[:limit]],
        "queries": [f"{context} manual workaround", f"{context} pricing alternatives", f"{context} feature request", f"{context} existing software workflow"],
        "questions": selected["questions"],
        "next_step": "Collect evidence from selected sources; planning alone does not validate demand.",
    }


def evaluate_candidate(candidate):
    """Stop at the first unresolved/failed gate; never let a score override failure."""
    gates = ["behavior", "buyer", "outcome", "delivery", "distribution", "economics", "experiment"]
    supplied = candidate.get("gates", {})
    for gate in gates:
        value = supplied.get(gate, {})
        status = value.get("status", "unknown")
        if status not in ("pass", "fail", "unknown"):
            raise ValueError(f"Invalid status for {gate}")
        if status == "fail":
            return {"decision": "stop", "gate": gate, "reason": value.get("reason", ""), "reopen_requires": value.get("reopen_requires", "New evidence addressing this failure")}
        if status == "unknown" or not value.get("evidence_ids"):
            return {"decision": "needs_evidence", "gate": gate, "reason": "Unknown or unsupported gate; do not advance"}
    test = candidate.get("experiment", {})
    if not all(test.get(field) for field in ["claim", "measurement", "abandon_condition", "deadline", "currency"]):
        return {"decision": "needs_evidence", "gate": "experiment", "reason": "Write claim, measurement, deadline, currency, and abandon condition before testing"}
    return {"decision": "ready_to_test", "reason": "Provisional gates passed; customer demand remains unvalidated until the experiment"}


def evidence_record(source_url, markdown, method, retrieved_at=None):
    return {
        "id": "ev_" + hashlib.sha256((source_url + "\n" + markdown).encode()).hexdigest()[:20],
        "source_url": source_url, "retrieved_at": retrieved_at or datetime.now(timezone.utc).isoformat(),
        "method": method, "content_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
        "evidence_status": "captured_unreviewed", "supports": [], "limitations": [],
        "origin_group": source_url, "publication_date": None,
        "note": "Capture proves retrieval, not accuracy, demand, or independent corroboration.",
    }


def save_capture(directory, record, markdown):
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    stem = record["id"]
    # Never overwrite an existing capture's retrieval metadata.
    for extension, content in [("md", markdown), ("json", json.dumps(record, indent=2, ensure_ascii=False))]:
        path = target / f"{stem}.{extension}"
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    return str(target / f"{stem}.json")

"""Run from the checkout: python -m idea_engine --help."""

import argparse
import json
import sys
from pathlib import Path

from .acquisition import AcquisitionError, capture_markdown
from .core import compile_prompt, evaluate_candidate, evidence_record, find_sources, make_plan, modes, read_json, save_capture
from .providers import screen_evidence, synthesize


def main(argv=None):
    parser = argparse.ArgumentParser(description="Idea Generator — research before conviction")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("modes", help="List ten discovery methods")
    search = sub.add_parser("sources", help="Search the local source registry")
    search.add_argument("query", nargs="?", default="")
    search.add_argument("--layer", choices=["market", "structural", "capability", "acquisition"])
    plan = sub.add_parser("plan", help="Create a research plan; no network or model calls")
    plan.add_argument("--mode", choices=[m["id"] for m in modes()], default="surprise")
    plan.add_argument("--seed", default="")
    plan.add_argument("--random-seed", type=int, default=0)
    plan.add_argument("--depth", choices=["quick", "standard", "deep"], default="standard")
    plan.add_argument("--out", help="Save plan JSON to a new file")
    compile_cmd = sub.add_parser("compile", help="Compile a standalone method prompt")
    compile_cmd.add_argument("--mode", choices=[m["id"] for m in modes()], required=True)
    compile_cmd.add_argument("--seed", default="")
    compile_cmd.add_argument("--evidence", help="JSON list of evidence records/excerpts to supply")
    compile_cmd.add_argument("--out")
    capture = sub.add_parser("capture", help="One public URL → Markdown through markdown.new")
    capture.add_argument("url")
    capture.add_argument("--public", action="store_true", help="Confirm this URL is public and may be sent to markdown.new")
    capture.add_argument("--out-dir", default="runs/evidence")
    imported = sub.add_parser("import", help="Import an existing Markdown capture with provenance")
    imported.add_argument("file")
    imported.add_argument("--url", required=True)
    imported.add_argument("--method", choices=["browser", "scraper", "manual", "local-conversion"], required=True)
    imported.add_argument("--out-dir", default="runs/evidence")
    gate = sub.add_parser("gate", help="Evaluate declared gates; does not verify evidence authenticity")
    gate.add_argument("file")
    model = sub.add_parser("synthesize", help="One OpenRouter call on a prepared prompt; no browsing")
    model.add_argument("file")
    model.add_argument("--live", action="store_true")
    model.add_argument("--out", required=True)
    screen = sub.add_parser("screen", help="One Jev request on supplied text")
    screen.add_argument("file")
    screen.add_argument("--live", action="store_true")
    screen.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        if getattr(args, "out", None) and Path(args.out).exists():
            raise ValueError("Output exists; use a new path to preserve the prior investigation")
        if args.command == "modes":
            result = modes()
        elif args.command == "sources":
            result = find_sources(args.query, args.layer)
        elif args.command == "plan":
            result = make_plan(args.mode, args.seed, args.random_seed, args.depth)
        elif args.command == "compile":
            evidence = read_json(args.evidence) if args.evidence else []
            if not isinstance(evidence, list):
                raise ValueError("Evidence input must be a JSON list")
            result = compile_prompt(args.mode, args.seed, evidence)
        elif args.command == "capture":
            markdown, headers = capture_markdown(args.url, args.public)
            record = evidence_record(args.url, markdown, "markdown.new")
            record["response_metadata"] = headers
            result = {"saved": save_capture(args.out_dir, record, markdown), "id": record["id"]}
        elif args.command == "import":
            markdown = Path(args.file).read_text(encoding="utf-8")
            if not markdown.strip():
                raise ValueError("Cannot import empty evidence")
            record = evidence_record(args.url, markdown, args.method)
            record["limitations"].append("Imported capture; acquisition time and completeness not independently verified")
            result = {"saved": save_capture(args.out_dir, record, markdown), "id": record["id"]}
        elif args.command == "gate":
            result = evaluate_candidate(read_json(args.file))
        elif args.command == "synthesize":
            result = synthesize(Path(args.file).read_text(encoding="utf-8"), args.live)
        else:
            result = screen_evidence(Path(args.file).read_text(encoding="utf-8"), args.live)
        output = result if isinstance(result, str) else json.dumps(result, indent=2, ensure_ascii=False)
        if getattr(args, "out", None):
            destination = Path(args.out)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("x", encoding="utf-8") as handle:
                handle.write(output + "\n")
            print(f"Saved {destination}")
        else:
            print(output)
        return 0
    except (ValueError, OSError, AcquisitionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

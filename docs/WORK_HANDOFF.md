# Work handoff

## Delivered
Ten method prompts + shared constitution, seeded research planner, searchable source registry, public Markdown capture/import, deterministic declared gates, explicit OpenRouter call and optional TypeSafe SDK screening. CLI and offline tests run from checkout. No dashboard yet.

## Located references
See data/integrations.json for user fork paths and inspected blob SHAs. markdown-new skill lives inside voice-website-agent-Markdown, not a confirmed standalone markdown.new fork. Official markdown.new docs supersede stale/speculative claims in that skill.

## Immediate next implementation
1. Add a catalog reader for Maliky docs/catalog/catalog.json and Every Awesome Repo data/catalog.json/data/tools.json; inspect exact schemas first.
2. Add durable run IDs/state, evidence linking and an enforceable usage/cost ledger before autonomous loops.
3. Add one bounded browser adapter using pinned agent-browser commands. Test on a public static page and a JS interaction; record failures and partial extraction.
4. Add structured synthesis output validation and citation support checks. V1 gate only checks declared IDs, not existence/quality.
5. Only after explicit key setup and authorized test spend, live-test provider payloads and evaluate Jev questions with held-out cases.
6. Build simple dashboard over the same records; do not implement a separate fake engine in the UI.

## Limits and security
No model keys provided or used. Network availability depends on runner configuration. No browser/scraper packages installed. CLI capture sends only public query-free URLs to third-party markdown.new and rejects private destinations, credentials, redirects and oversized responses. It is not a general-purpose public fetch endpoint. V1 does not persist model request payloads, automatically validate citations, schedule jobs, enforce monetary caps across runs, synchronize catalogs or run the private Gauntlet.

Validation instructions: python scripts/validate.py; python -m unittest discover -s tests -v; CLI smoke commands in README. Live connectivity remains separate from mocked transport checks.

## Verification outcome
Local schema/catalog checks and 22 offline tests passed. A real public Markdown capture was attempted; local destination DNS could not be verified in this executor, so the adapter failed closed before contacting markdown.new. No successful live extraction is claimed. Source sites and official interfaces were inspected through available web research tools.

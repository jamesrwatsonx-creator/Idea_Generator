# Idea Generator

**Find what is worth building. Discover what already exists to build it. Test what must be true.**

Research-first app ideation with ten entry points, seeded Surprise me, shared evidence and explicit stop conditions. Home UX: **Surprise me / Start with something / Explore all methods**. Go deeper into Demand, Product, Build, Challenge or Test.

## Current state
Working Python research foundation, not a finished dashboard or autonomous researcher. No runtime dependencies for local planning, search, compilation, import, gates or Markdown capture. OpenRouter single-call synthesis and optional Jev screening are implemented but not live-validated. Browser agents, Apify, catalog sync and reverse-engineering tools are registered/planned, not active integrations. No fake research results.

## Run from this checkout (Python 3.10+)

```bash
python -m idea_engine modes
python -m idea_engine sources "markdown browser"
python -m idea_engine sources --layer market
python -m idea_engine plan --random-seed 42 --out runs/plan.json
python -m idea_engine plan --mode compose-apps --seed "calendar + client notes + tasks" --depth deep
python -m idea_engine compile --mode expand --seed "an invoicing application" --out runs/prompt.md
python -m idea_engine capture https://example.com --public --out-dir runs/evidence
python -m idea_engine import captured.md --url https://example.com --method browser
python -m idea_engine gate examples/candidate.json
python scripts/validate.py
python -m unittest discover -s tests -v
```

Capture explicitly sends a public URL to markdown.new. It saves Markdown plus content hash, source URL, method and retrieval metadata. Imported files remain unreviewed evidence. Plans and compiled prompts do not browse.

## Ten discovery methods
- **Surprise me** (`surprise`): Discover unexpected opportunities through seeded exploration.
- **Improve an existing app** (`expand`): Investigate the decisions around one application.
- **Combine existing apps** (`compose-apps`): Recover valuable handoffs between products.
- **Build from a repository** (`repo`): Find applications for a specific technical capability.
- **Find an underserved buyer** (`arbitrage`): Investigate structural exclusion by pricing and delivery.
- **Remove manual work** (`workaround`): Find a repetitive tax worth removing or assisting.
- **Connect data into a decision** (`data-decision`): Find a useful join that changes a decision.
- **Exploit a recent change** (`window`): Find newly viable offers and migration needs.
- **Transfer across industries** (`transfer`): Move a proven mechanism to a new context.
- **Compose from my capabilities** (`inventory`): Search catalogs for useful combinations without confusing supply with demand.

## Models
Configure keys through environment settings or a secret store, never chat or commits. `.env.example` documents names; no automatic dotenv loader. Choose OPENROUTER_MODEL explicitly. Install optional `typesafe-sdk` according to current TypeSafe docs before screening. Configure provider-side spending limits. V1 only makes one explicit call per command; it does not enforce a cross-run monetary cap.

```bash
python -m idea_engine synthesize runs/prompt.md --live --out runs/hypothesis.json
python -m idea_engine screen captured.md --live --out runs/screen.json
```

Synthesis only sees supplied text; it does not browse. Jev judgments are probabilities about bounded questions, not business verdicts. No live request was performed during this implementation.

## Sources and existing projects
See [browseable source catalog](docs/SOURCES.md), [source registry](data/sources.json), [integration provenance](data/integrations.json), [research standards](docs/RESEARCH.md) and [acquisition strategy](docs/ACQUISITION.md). NoSignups is prioritized for discovery; Our World in Data supplies structural context. Market need, commercial demand and technical feasibility remain distinct.

Reuse Every Awesome Repo for external discovery and Maliky for available assets. Gauntlet supplies challenge/constraint principles; its private constitution stays outside this public repository. Third-party tools are linked, not vendored or automatically executed.

## Next work
[Work handoff](docs/WORK_HANDOFF.md) · [Architecture](docs/ARCHITECTURE.md) · [UX](docs/UX.md) · [Roadmap](docs/ROADMAP.md)

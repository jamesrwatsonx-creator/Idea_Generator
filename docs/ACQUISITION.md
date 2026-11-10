# Browser agents, scraping and Markdown

## Located user references
- voice-website-agent-Markdown contains skills/markdown-new/SKILL.md. See data/integrations.json for exact inspected blob. Do not copy its speculative examples or universal format/support claims into implementation.
- Ghl-and-voice-idea-agent-browser is the located agent-browser fork.
- browser-use is an alternative fork; fork runtime not inspected.
- defuddle extracts main HTML/Markdown; markitdown converts supported document formats.

## markdown.new
Official docs: https://markdown.new/
Documented POST: {"url":"https://example.com","method":"auto","retain_images":false}. V1 implements that path, rejects non-public destinations and query-bearing URLs, limits response bytes, requires explicit --public and stores provenance. The service receives the URL. Use only public, nonsensitive targets with permitted access. It cannot convert all information; authenticated/paywalled sources are unsupported. Browser rendering, truncation and limits are source/service-specific. Homepage crawl-limit statements conflict; do not hardcode them. V1 does not crawl.

Local alternatives: browser snapshot plus Defuddle; supported local documents through MarkItDown. These are registered references, not installed adapters. Import their output using the CLI and explicitly label acquisition method. Preserve relevant comments, tables and metadata when extraction removes them.

## Browser agent escalation
Use agent-browser for selected interactions/snapshots only when static extraction cannot answer a named question. Browser Use is a candidate alternative. Pin/test versions and install browsers separately. Do not shell-execute arbitrary model-generated commands. Future worker needs structured actions, domain checks, bounded steps, read-only defaults, isolated profiles, screenshot/capture provenance and explicit external mutation approval. No credentials, logins or private browsing state by default.

## Scraping
Prefer official APIs/downloads. Apify Actors and Crawl4AI are optional backends, not blanket access rights. Inspect source terms, robots directives, schemas, extraction completeness and paid costs. Set page/concurrency/retry limits. On block or missing access, record a blocker; never convert it into no demand or bypass restrictions. TrustMRR API policy prohibits cloning businesses and bulk republication.

## Verification
Live extraction and provider requests have not been tested with user keys. Unit tests use controlled transports. Service documentation checked 2026-11-09 is evidence of the documented interface, not an uptime or completeness guarantee.

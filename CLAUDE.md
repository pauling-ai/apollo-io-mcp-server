# Apollo MCP Server — Claude Instructions

## Project

MCP server for Apollo.io contact and company enrichment. REST API client — no browser, no scraping.

## Package

- Package: `apollo_mcp_server/`
- Entry point: `apollo-mcp` → `apollo_mcp_server.cli_main:main`
- Tests: `tests/`

## Commands

```bash
uv sync                        # install dependencies
uv run pytest                  # run tests
uv run ruff check .            # lint
uv run apollo-mcp --status     # verify API key
```

## Tools

| Tool | Apollo Endpoint |
|------|----------------|
| `find_person` | `POST /api/v1/people/match` |
| `enrich_by_linkedin` | `POST /api/v1/people/match` |
| `search_company` | `POST /api/v1/mixed_people/search` |
| `get_company` | `GET /api/v1/organizations/enrich` |

## Key Decisions

- `APOLLO_API_KEY` env var (not `APOLLO_IO_API_KEY`)
- `include_phone=False` by default — phone costs extra Apollo credits
- `search_company` auto-detects domain vs name input (dot + no spaces = domain)
- Responses are filtered — only return fields useful to Claude, not raw Apollo blobs
- Hard fail with clear error on missing API key or quota exhaustion

## Testing

Mock httpx calls using `pytest-httpx`. Patch `get_client()` for tool-level tests.

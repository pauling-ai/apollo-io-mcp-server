# Apollo MCP Server

MCP server for [Apollo.io](https://apollo.io) contact and company enrichment. Gives Claude direct access to Apollo's people and organization data — find emails, enrich LinkedIn profiles, and discover contacts at target companies.

## Tools

### People
| Tool | Description |
|------|-------------|
| `find_person` | Find a person's email by name and company. Optional job title improves match accuracy. |
| `enrich_by_linkedin` | Look up email and contact details from a LinkedIn profile URL. More accurate than name search when you already have the URL. |

### Companies
| Tool | Description |
|------|-------------|
| `search_company` | Find people who work at a given company. Accepts company name or domain. Optional title filter (e.g. "CEO", "Head of Chemistry"). |
| `get_company` | Get firmographic details about a company: industry, employee count, description. Useful for qualifying leads. |

All tools accept a company name or domain — domain matching is more precise when available.

## Setup

**Prerequisites:** Python 3.12+ and [uv](https://docs.astral.sh/uv/) installed

```bash
# 1. Run setup — saves your API key to ~/.apollo-mcp/.env
uvx --from git+https://github.com/pauling-ai/apollo-mcp-server apollo-mcp --setup
```

That's it. The key is stored in `~/.apollo-mcp/.env` and loaded automatically every time the server starts — no need to pass it in `.mcp.json` or set environment variables.

## Claude Code / MCP Configuration

After running `--setup`, add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "apollo": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/pauling-ai/apollo-mcp-server", "apollo-mcp"],
      "env": {}
    }
  }
}
```

No API key in the config — it's read from `~/.apollo-mcp/.env` automatically.

## CLI Options

- `--setup` — Save API key to `~/.apollo-mcp/.env` and verify it works
- `--status` — Verify API key is valid and exit
- `--log-level {DEBUG,INFO,WARNING,ERROR}` — Logging level (default: WARNING)
- `--transport {stdio,streamable-http}` — Transport mode (default: stdio)
- `--version` — Print version and exit

## Apollo Credits

Apollo charges credits for enrichment calls. Key things to know:

- `find_person` and `enrich_by_linkedin` consume enrichment credits per call
- `include_phone=True` costs additional credits — only use when needed
- `search_company` uses search credits (cheaper than enrichment)
- `get_company` uses organization enrichment credits
- Free tier is limited — check your plan at [Apollo billing](https://app.apollo.io/#/settings/billing)

## Troubleshooting

**API key not found:** Run `apollo-mcp --setup` to save your key to `~/.apollo-mcp/.env`.

**API key rejected (401):** Re-run `apollo-mcp --setup` with a fresh key from [developer.apollo.io/#/keys](https://developer.apollo.io/#/keys).

**Quota exhausted (429):** You've hit Apollo's rate limit or used all credits on your plan. Check usage at Apollo billing.

**Person not found:** Apollo returns `found: false` when no match exists. Try `enrich_by_linkedin` with the LinkedIn URL instead of `find_person` — it's more accurate.

**Company search returns no results:** Try the company domain instead of name (e.g. `acmepharma.com` instead of `Acme Pharma`).

## Notes

- Responses are filtered to return only fields useful to Claude — not raw Apollo API blobs
- `find_person` without a title may match the wrong person when names are common — provide `title` when available
- Phone is excluded by default to avoid unnecessary credit usage — pass `include_phone=True` when needed

## License

MIT — see [LICENSE](LICENSE)

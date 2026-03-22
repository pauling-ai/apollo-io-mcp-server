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
# 1. Clone the repo
git clone https://github.com/pauling-ai/apollo-mcp-server
cd apollo-mcp-server

# 2. Install dependencies
uv sync

# 3. Get your Apollo API key
# Go to: https://app.apollo.io/#/settings/integrations/api_keys
# Create a key and copy it

# 4. Set the API key
export APOLLO_API_KEY=your_key_here
# Or add it to a .env file in the project root:
echo "APOLLO_API_KEY=your_key_here" > .env

# 5. Verify it works
uv run apollo-mcp --status
```

## Installing into another project

```bash
# With uv (recommended)
uv pip install -e /path/to/apollo-mcp-server

# Or with pip
pip install -e /path/to/apollo-mcp-server
```

## Claude Code / MCP Configuration

After installing, add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "apollo": {
      "type": "stdio",
      "command": "/path/to/venv/bin/apollo-mcp",
      "env": {
        "APOLLO_API_KEY": "your_key_here",
        "LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

Or run directly from the repo with `uv` (no install needed):

```json
{
  "mcpServers": {
    "apollo": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/path/to/apollo-mcp-server", "run", "apollo-mcp"],
      "env": {
        "APOLLO_API_KEY": "your_key_here"
      }
    }
  }
}
```

## CLI Options

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

**`APOLLO_API_KEY` not set:** Run `export APOLLO_API_KEY=your_key` or add it to a `.env` file.

**API key rejected (401):** Verify your key at [Apollo API settings](https://app.apollo.io/#/settings/integrations/api_keys). Keys can be revoked or have restricted permissions.

**Quota exhausted (429):** You've hit Apollo's rate limit or used all credits on your plan. Check usage at Apollo billing.

**Person not found:** Apollo returns `found: false` when no match exists. Try `enrich_by_linkedin` with the LinkedIn URL instead of `find_person` — it's more accurate.

**Company search returns no results:** Try the company domain instead of name (e.g. `acmepharma.com` instead of `Acme Pharma`).

## Notes

- Responses are filtered to return only fields useful to Claude — not raw Apollo API blobs
- `find_person` without a title may match the wrong person when names are common — provide `title` when available
- Phone is excluded by default to avoid unnecessary credit usage — pass `include_phone=True` when needed

## License

MIT — see [LICENSE](LICENSE)

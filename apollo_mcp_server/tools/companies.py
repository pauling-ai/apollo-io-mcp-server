"""Company tools: search_company, get_company."""

import logging
from typing import Any

from fastmcp import FastMCP

from apollo_mcp_server.client import get_client

logger = logging.getLogger(__name__)


def _is_domain(value: str) -> bool:
    """Heuristic: 'acme.com' is a domain, 'Acme Corp' is a name."""
    return "." in value and " " not in value.strip()


def _format_contact(person: dict[str, Any]) -> dict[str, Any]:
    """Convert a raw Apollo person object to a minimal contact record."""
    return {
        "name": person.get("name"),
        "email": person.get("email"),
        "email_status": person.get("email_status"),
        "title": person.get("title"),
        "linkedin_url": person.get("linkedin_url"),
    }


def register_company_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        title="Search Company Contacts",
        annotations={"readOnlyHint": True},
        tags={"companies"},
    )
    async def search_company(
        company: str,
        title_filter: str | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Find people who work at a given company.

        Accepts either a company name (e.g. "Acme Pharma") or domain
        (e.g. "acme.com") — domain matching is more precise when available.

        Optionally filter by job title (e.g. "Head of Chemistry", "CEO").
        Returns up to max_results contacts with name, email, email_status,
        title, and LinkedIn URL.
        """
        client = get_client()

        payload: dict[str, Any] = {"per_page": min(max_results, 100), "page": 1}

        if _is_domain(company):
            payload["q_organization_domains_list"] = [company]
        else:
            payload["organization_names"] = [company]

        if title_filter:
            payload["person_titles"] = [title_filter]

        data = await client.people_search(payload)
        people = data.get("people") or []
        return [_format_contact(p) for p in people]

    @mcp.tool(
        title="Get Company Info",
        annotations={"readOnlyHint": True},
        tags={"companies"},
    )
    async def get_company(
        company: str,
    ) -> dict[str, Any]:
        """
        Get firmographic details about a company.

        Accepts either a company name (e.g. "Acme Pharma") or domain
        (e.g. "acme.com") — domain matching is more precise when available.

        Returns name, domain, website, industry, employee count, and a
        short description. Useful for qualifying leads before outreach.
        """
        client = get_client()

        if _is_domain(company):
            params: dict[str, Any] = {"domain": company}
        else:
            params = {"name": company}

        data = await client.organization_enrich(params)
        org = data.get("organization")
        if not org:
            return {"found": False, "company": company}

        return {
            "found": True,
            "name": org.get("name"),
            "domain": org.get("primary_domain"),
            "website": org.get("website_url"),
            "industry": org.get("industry"),
            "employees": org.get("estimated_num_employees"),
            "description": org.get("short_description"),
        }

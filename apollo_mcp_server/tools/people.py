"""People enrichment tools: find_person, enrich_by_linkedin."""

import logging
from typing import Any

from fastmcp import FastMCP

from apollo_mcp_server.client import get_client

logger = logging.getLogger(__name__)


def _format_person(person: dict[str, Any], include_phone: bool = False) -> dict[str, Any]:
    """Convert a raw Apollo person object into a clean, minimal record."""
    result: dict[str, Any] = {
        "name": person.get("name"),
        "email": person.get("email"),
        "email_status": person.get("email_status"),
        "title": person.get("title"),
        "company": (person.get("organization") or {}).get("name"),
        "linkedin_url": person.get("linkedin_url"),
    }
    if include_phone:
        phones = person.get("phone_numbers") or []
        result["phone"] = phones[0].get("raw_number") if phones else None
    return result


def register_people_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        title="Find Person",
        annotations={"readOnlyHint": True},
        tags={"people"},
    )
    async def find_person(
        name: str,
        company: str,
        title: str | None = None,
        include_phone: bool = False,
    ) -> dict[str, Any]:
        """
        Find a person's email and contact details by name and company.

        COSTS APOLLO CREDITS — only call when you actually need the email.
        Do not call speculatively or in bulk without user confirmation.

        Providing a job title improves match accuracy when multiple people
        share the same name at a company.

        Returns name, email, email_status (verified/likely_to_engage/unverified),
        title, company, and LinkedIn URL. Set include_phone=True to also return
        a phone number (costs extra Apollo credits).
        """
        client = get_client()
        payload: dict[str, Any] = {
            "name": name,
            "organization_name": company,
            "reveal_phone_number": include_phone,
        }
        if title:
            payload["title"] = title

        data = await client.people_match(payload)
        person = data.get("person")
        if not person:
            return {"found": False, "name": name, "company": company}

        result = _format_person(person, include_phone=include_phone)
        result["found"] = True
        return result

    @mcp.tool(
        title="Enrich by LinkedIn URL",
        annotations={"readOnlyHint": True},
        tags={"people"},
    )
    async def enrich_by_linkedin(
        linkedin_url: str,
        include_phone: bool = False,
    ) -> dict[str, Any]:
        """
        Look up a person's email and contact details from their LinkedIn profile URL.

        COSTS APOLLO CREDITS — only call when you actually need the email.
        Do not call speculatively or in bulk without user confirmation.

        More accurate than find_person when you already have the LinkedIn URL,
        since it matches on a unique identifier rather than name + company.

        Returns name, email, email_status, title, company, and LinkedIn URL.
        Set include_phone=True to also return a phone number (costs extra Apollo credits).
        """
        client = get_client()
        payload: dict[str, Any] = {
            "linkedin_url": linkedin_url,
            "reveal_phone_number": include_phone,
        }

        data = await client.people_match(payload)
        person = data.get("person")
        if not person:
            return {"found": False, "linkedin_url": linkedin_url}

        result = _format_person(person, include_phone=include_phone)
        result["found"] = True
        return result

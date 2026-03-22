"""Shared fixtures for Apollo MCP Server tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from apollo_mcp_server.client import ApolloClient


@pytest.fixture
def mock_client() -> MagicMock:
    """A mock ApolloClient with AsyncMock methods."""
    client = MagicMock(spec=ApolloClient)
    client.people_match = AsyncMock()
    client.people_search = AsyncMock()
    client.organization_enrich = AsyncMock()
    client.check_auth = AsyncMock(return_value=True)
    return client


PERSON_FIXTURE = {
    "id": "abc123",
    "name": "Jane Smith",
    "email": "jane@acmepharma.com",
    "email_status": "verified",
    "title": "Head of Computational Chemistry",
    "linkedin_url": "https://www.linkedin.com/in/janesmith/",
    "phone_numbers": [{"raw_number": "+1-555-123-4567", "type": "work"}],
    "organization": {
        "name": "Acme Pharma",
        "website_url": "https://acmepharma.com",
        "primary_domain": "acmepharma.com",
    },
}

COMPANY_FIXTURE = {
    "id": "org123",
    "name": "Acme Pharma",
    "website_url": "https://acmepharma.com",
    "primary_domain": "acmepharma.com",
    "industry": "biotechnology",
    "estimated_num_employees": 250,
    "short_description": "A leading computational chemistry company.",
}

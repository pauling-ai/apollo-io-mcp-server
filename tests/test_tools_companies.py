"""Tests for company tools: search_company, get_company."""

import pytest
from unittest.mock import patch
from fastmcp import FastMCP

from apollo_mcp_server.tools.companies import register_company_tools, _is_domain
from tests.conftest import PERSON_FIXTURE, COMPANY_FIXTURE


async def get_tool_fn(mcp: FastMCP, name: str):
    tool = await mcp.get_tool(name)
    if tool is None:
        raise ValueError(f"Tool '{name}' not found")
    return tool.fn


@pytest.fixture
def mcp_with_company_tools() -> FastMCP:
    mcp = FastMCP("test")
    register_company_tools(mcp)
    return mcp


class TestIsDomain:
    def test_domain_detected(self):
        assert _is_domain("acme.com") is True
        assert _is_domain("acmepharma.io") is True
        assert _is_domain("sub.domain.org") is True

    def test_name_not_domain(self):
        assert _is_domain("Acme Pharma") is False
        assert _is_domain("Acme Corp") is False
        assert _is_domain("AcmePharma") is False  # no dot


class TestSearchCompany:
    async def test_returns_contacts(self, mcp_with_company_tools, mock_client):
        mock_client.people_search.return_value = {
            "people": [PERSON_FIXTURE, {**PERSON_FIXTURE, "name": "Bob Jones"}],
            "pagination": {"total_entries": 2},
        }

        fn = await get_tool_fn(mcp_with_company_tools, "search_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            results = await fn("Acme Pharma")

        assert len(results) == 2
        assert results[0]["name"] == "Jane Smith"
        assert results[0]["email"] == "jane@acmepharma.com"
        assert results[0]["email_status"] == "verified"
        assert results[0]["title"] == "Head of Computational Chemistry"
        assert results[0]["linkedin_url"] == "https://www.linkedin.com/in/janesmith/"
        assert "phone" not in results[0]

    async def test_uses_organization_names_for_company_name(self, mcp_with_company_tools, mock_client):
        mock_client.people_search.return_value = {"people": []}

        fn = await get_tool_fn(mcp_with_company_tools, "search_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            await fn("Acme Pharma")

        payload = mock_client.people_search.call_args[0][0]
        assert payload["organization_names"] == ["Acme Pharma"]
        assert "q_organization_domains_list" not in payload

    async def test_uses_domain_filter_for_domain_input(self, mcp_with_company_tools, mock_client):
        mock_client.people_search.return_value = {"people": []}

        fn = await get_tool_fn(mcp_with_company_tools, "search_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            await fn("acmepharma.com")

        payload = mock_client.people_search.call_args[0][0]
        assert payload["q_organization_domains_list"] == ["acmepharma.com"]
        assert "organization_names" not in payload

    async def test_title_filter(self, mcp_with_company_tools, mock_client):
        mock_client.people_search.return_value = {"people": [PERSON_FIXTURE]}

        fn = await get_tool_fn(mcp_with_company_tools, "search_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            await fn("Acme Pharma", title_filter="Head of Chemistry")

        payload = mock_client.people_search.call_args[0][0]
        assert payload["person_titles"] == ["Head of Chemistry"]

    async def test_no_title_filter_by_default(self, mcp_with_company_tools, mock_client):
        mock_client.people_search.return_value = {"people": []}

        fn = await get_tool_fn(mcp_with_company_tools, "search_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            await fn("Acme Pharma")

        payload = mock_client.people_search.call_args[0][0]
        assert "person_titles" not in payload

    async def test_max_results_respected(self, mcp_with_company_tools, mock_client):
        mock_client.people_search.return_value = {"people": []}

        fn = await get_tool_fn(mcp_with_company_tools, "search_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            await fn("Acme Pharma", max_results=5)

        payload = mock_client.people_search.call_args[0][0]
        assert payload["per_page"] == 5

    async def test_empty_results(self, mcp_with_company_tools, mock_client):
        mock_client.people_search.return_value = {"people": [], "pagination": {"total_entries": 0}}

        fn = await get_tool_fn(mcp_with_company_tools, "search_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            results = await fn("Unknown Corp")

        assert results == []


class TestGetCompany:
    async def test_found_by_name(self, mcp_with_company_tools, mock_client):
        mock_client.organization_enrich.return_value = {"organization": COMPANY_FIXTURE}

        fn = await get_tool_fn(mcp_with_company_tools, "get_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            result = await fn("Acme Pharma")

        assert result["found"] is True
        assert result["name"] == "Acme Pharma"
        assert result["domain"] == "acmepharma.com"
        assert result["industry"] == "biotechnology"
        assert result["employees"] == 250
        assert result["description"] == "A leading computational chemistry company."

    async def test_found_by_domain(self, mcp_with_company_tools, mock_client):
        mock_client.organization_enrich.return_value = {"organization": COMPANY_FIXTURE}

        fn = await get_tool_fn(mcp_with_company_tools, "get_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            await fn("acmepharma.com")

        params = mock_client.organization_enrich.call_args[0][0]
        assert params == {"domain": "acmepharma.com"}

    async def test_uses_name_param_for_company_name(self, mcp_with_company_tools, mock_client):
        mock_client.organization_enrich.return_value = {"organization": COMPANY_FIXTURE}

        fn = await get_tool_fn(mcp_with_company_tools, "get_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            await fn("Acme Pharma")

        params = mock_client.organization_enrich.call_args[0][0]
        assert params == {"name": "Acme Pharma"}

    async def test_not_found(self, mcp_with_company_tools, mock_client):
        mock_client.organization_enrich.return_value = {"organization": None}

        fn = await get_tool_fn(mcp_with_company_tools, "get_company")
        with patch("apollo_mcp_server.tools.companies.get_client", return_value=mock_client):
            result = await fn("Unknown Corp")

        assert result["found"] is False
        assert result["company"] == "Unknown Corp"

"""Tests for people tools: find_person, enrich_by_linkedin."""

import pytest
from unittest.mock import patch
from fastmcp import FastMCP

from apollo_mcp_server.tools.people import register_people_tools
from tests.conftest import PERSON_FIXTURE


async def get_tool_fn(mcp: FastMCP, name: str):
    tool = await mcp.get_tool(name)
    if tool is None:
        raise ValueError(f"Tool '{name}' not found")
    return tool.fn


@pytest.fixture
def mcp_with_people_tools() -> FastMCP:
    mcp = FastMCP("test")
    register_people_tools(mcp)
    return mcp


class TestFindPerson:
    async def test_found(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}

        fn = await get_tool_fn(mcp_with_people_tools, "find_person")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            result = await fn("Jane Smith", "Acme Pharma")

        assert result["found"] is True
        assert result["email"] == "jane@acmepharma.com"
        assert result["email_status"] == "verified"
        assert result["title"] == "Head of Computational Chemistry"
        assert result["company"] == "Acme Pharma"
        assert result["linkedin_url"] == "https://www.linkedin.com/in/janesmith/"
        assert "phone" not in result

    async def test_found_with_title(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}

        fn = await get_tool_fn(mcp_with_people_tools, "find_person")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            await fn("Jane Smith", "Acme Pharma", title="Head of Computational Chemistry")

        call_payload = mock_client.people_match.call_args[0][0]
        assert call_payload["title"] == "Head of Computational Chemistry"

    async def test_not_found(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": None}

        fn = await get_tool_fn(mcp_with_people_tools, "find_person")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            result = await fn("Unknown Person", "Unknown Corp")

        assert result["found"] is False
        assert result["name"] == "Unknown Person"
        assert result["company"] == "Unknown Corp"

    async def test_include_phone(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}

        fn = await get_tool_fn(mcp_with_people_tools, "find_person")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            result = await fn("Jane Smith", "Acme Pharma", include_phone=True)

        assert result["phone"] == "+1-555-123-4567"
        call_payload = mock_client.people_match.call_args[0][0]
        assert call_payload["reveal_phone_number"] is True

    async def test_no_phone_by_default(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}

        fn = await get_tool_fn(mcp_with_people_tools, "find_person")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            result = await fn("Jane Smith", "Acme Pharma")

        assert "phone" not in result
        call_payload = mock_client.people_match.call_args[0][0]
        assert call_payload["reveal_phone_number"] is False

    async def test_payload_contains_name_and_company(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}

        fn = await get_tool_fn(mcp_with_people_tools, "find_person")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            await fn("Jane Smith", "Acme Pharma")

        payload = mock_client.people_match.call_args[0][0]
        assert payload["name"] == "Jane Smith"
        assert payload["organization_name"] == "Acme Pharma"

    async def test_no_title_not_in_payload(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}

        fn = await get_tool_fn(mcp_with_people_tools, "find_person")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            await fn("Jane Smith", "Acme Pharma")

        payload = mock_client.people_match.call_args[0][0]
        assert "title" not in payload

    async def test_person_missing_optional_fields(self, mcp_with_people_tools, mock_client):
        sparse_person = {"name": "Jane Smith", "email": None, "email_status": None}
        mock_client.people_match.return_value = {"person": sparse_person}

        fn = await get_tool_fn(mcp_with_people_tools, "find_person")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            result = await fn("Jane Smith", "Acme Pharma")

        assert result["found"] is True
        assert result["email"] is None
        assert result["company"] is None
        assert result["linkedin_url"] is None


class TestEnrichByLinkedIn:
    async def test_found(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}

        fn = await get_tool_fn(mcp_with_people_tools, "enrich_by_linkedin")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            result = await fn("https://www.linkedin.com/in/janesmith/")

        assert result["found"] is True
        assert result["email"] == "jane@acmepharma.com"

    async def test_payload_contains_linkedin_url(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}
        url = "https://www.linkedin.com/in/janesmith/"

        fn = await get_tool_fn(mcp_with_people_tools, "enrich_by_linkedin")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            await fn(url)

        payload = mock_client.people_match.call_args[0][0]
        assert payload["linkedin_url"] == url

    async def test_not_found(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": None}

        fn = await get_tool_fn(mcp_with_people_tools, "enrich_by_linkedin")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            result = await fn("https://www.linkedin.com/in/nobody/")

        assert result["found"] is False
        assert "linkedin_url" in result

    async def test_include_phone(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}

        fn = await get_tool_fn(mcp_with_people_tools, "enrich_by_linkedin")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            result = await fn("https://www.linkedin.com/in/janesmith/", include_phone=True)

        assert result["phone"] == "+1-555-123-4567"

    async def test_no_phone_by_default(self, mcp_with_people_tools, mock_client):
        mock_client.people_match.return_value = {"person": PERSON_FIXTURE}

        fn = await get_tool_fn(mcp_with_people_tools, "enrich_by_linkedin")
        with patch("apollo_mcp_server.tools.people.get_client", return_value=mock_client):
            result = await fn("https://www.linkedin.com/in/janesmith/")

        assert "phone" not in result

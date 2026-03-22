"""Tests for ApolloClient HTTP calls."""

import pytest
from pytest_httpx import HTTPXMock

from apollo_mcp_server.client import ApolloClient, ApolloError

BASE_URL = "https://api.apollo.io/api/v1"
API_KEY = "test-key"


@pytest.fixture
def client() -> ApolloClient:
    return ApolloClient(api_key=API_KEY, base_url=BASE_URL)


class TestPeopleMatch:
    async def test_success(self, client: ApolloClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/people/match",
            method="POST",
            json={"person": {"name": "Jane Smith", "email": "jane@acme.com"}},
        )
        result = await client.people_match({"name": "Jane Smith"})
        assert result["person"]["email"] == "jane@acme.com"

    async def test_invalid_api_key_raises(self, client: ApolloClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(url=f"{BASE_URL}/people/match", method="POST", status_code=401)
        with pytest.raises(ApolloError) as exc_info:
            await client.people_match({"name": "Jane Smith"})
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)

    async def test_rate_limit_raises(self, client: ApolloClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(url=f"{BASE_URL}/people/match", method="POST", status_code=429)
        with pytest.raises(ApolloError) as exc_info:
            await client.people_match({})
        assert exc_info.value.status_code == 429
        assert "quota" in str(exc_info.value).lower()

    async def test_person_not_found_returns_empty(self, client: ApolloClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/people/match",
            method="POST",
            json={"person": None, "status": "success"},
        )
        result = await client.people_match({"name": "Unknown Person"})
        assert result["person"] is None


class TestPeopleSearch:
    async def test_success(self, client: ApolloClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mixed_people/search",
            method="POST",
            json={"people": [{"name": "Bob Jones"}], "pagination": {"total_entries": 1}},
        )
        result = await client.people_search({"organization_names": ["Acme"]})
        assert len(result["people"]) == 1

    async def test_empty_results(self, client: ApolloClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mixed_people/search",
            method="POST",
            json={"people": [], "pagination": {"total_entries": 0}},
        )
        result = await client.people_search({"organization_names": ["Unknown Co"]})
        assert result["people"] == []


class TestOrganizationEnrich:
    async def test_success(self, client: ApolloClient, httpx_mock: HTTPXMock):
        # Don't filter by URL — query params make exact matching fragile
        httpx_mock.add_response(
            json={"organization": {"name": "Acme Pharma", "primary_domain": "acme.com"}},
        )
        result = await client.organization_enrich({"domain": "acme.com"})
        assert result["organization"]["name"] == "Acme Pharma"

    async def test_not_found_returns_null_org(self, client: ApolloClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(json={"organization": None})
        result = await client.organization_enrich({"domain": "unknown.xyz"})
        assert result["organization"] is None


class TestCheckAuth:
    async def test_valid_key(self, client: ApolloClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mixed_people/search",
            method="POST",
            json={"people": []},
        )
        assert await client.check_auth() is True

    async def test_invalid_key(self, client: ApolloClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/mixed_people/search",
            method="POST",
            status_code=401,
        )
        assert await client.check_auth() is False

"""Apollo.io API client."""

import logging
from typing import Any

import httpx

from apollo_mcp_server.config import get_config

logger = logging.getLogger(__name__)

_client: "ApolloClient | None" = None


def get_client() -> "ApolloClient":
    global _client
    if _client is None:
        config = get_config()
        _client = ApolloClient(api_key=config.api_key, base_url=config.base_url)
    return _client


class ApolloError(Exception):
    """Raised when the Apollo API returns an error."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"Apollo API error {status_code}: {message}")


class ApolloClient:
    def __init__(self, api_key: str, base_url: str = "https://api.apollo.io/api/v1"):
        self.base_url = base_url
        self._headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "cache-control": "no-cache",
            "x-api-key": api_key,
        }

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise ApolloError(401, "Invalid API key. Check your APOLLO_API_KEY.")
        if response.status_code == 422:
            raise ApolloError(422, "Unprocessable request. Check your input parameters.")
        if response.status_code == 429:
            raise ApolloError(429, "Apollo API rate limit or quota exhausted.")
        if response.status_code >= 400:
            raise ApolloError(response.status_code, response.text)

    async def people_match(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /people/match — enrich a single person."""
        async with httpx.AsyncClient() as http:
            response = await http.post(
                f"{self.base_url}/people/match",
                json=payload,
                headers=self._headers,
            )
        logger.debug("people/match status=%s", response.status_code)
        self._raise_for_status(response)
        return response.json()

    async def people_search(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /mixed_people/api_search — search people with filters."""
        async with httpx.AsyncClient() as http:
            response = await http.post(
                f"{self.base_url}/mixed_people/api_search",
                json=payload,
                headers=self._headers,
            )
        logger.debug("mixed_people/api_search status=%s", response.status_code)
        self._raise_for_status(response)
        return response.json()

    async def organization_enrich(self, params: dict[str, Any]) -> dict[str, Any]:
        """GET /organizations/enrich — enrich a single company."""
        async with httpx.AsyncClient() as http:
            response = await http.get(
                f"{self.base_url}/organizations/enrich",
                params=params,
                headers=self._headers,
            )
        logger.debug("organizations/enrich status=%s", response.status_code)
        self._raise_for_status(response)
        return response.json()

    async def check_auth(self) -> bool:
        """Verify the API key is valid.

        Returns False only on 401 (invalid key). Any other response —
        including 403 (plan restriction) or 422 (bad params) — means
        the key was accepted by Apollo.
        """
        async with httpx.AsyncClient() as http:
            response = await http.post(
                f"{self.base_url}/people/match",
                json={"name": "test"},
                headers=self._headers,
            )
        logger.debug("check_auth status=%s", response.status_code)
        return response.status_code != 401

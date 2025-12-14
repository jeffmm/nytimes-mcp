"""NYT API client for making requests to the New York Times API."""

import asyncio
from datetime import datetime
from typing import Any

import httpx

from nytimes_mcp.config import settings


def filter_params(params: dict[str, Any]) -> dict[str, Any]:
    """
    Remove None, empty strings, and 0 values from parameters.

    This keeps API requests minimal by only sending meaningful parameters.
    """
    return {k: v for k, v in params.items() if v is not None and v != "" and v != 0}


class NytClient:
    client: httpx.AsyncClient
    last_call: datetime

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.last_call = datetime.min
        self.api_key = settings.nyt_api_key

    async def make_nyt_request(self, endpoint: str, params: dict[str, Any]) -> dict:
        """
        Make a request to the NYT API with parameter filtering and error handling.

        Args:
            client: httpx AsyncClient instance
            endpoint: API endpoint path (e.g., "search/v2/articlesearch.json")
            params: Query parameters dict
            api_key: NYT API key

        Returns:
            Response JSON as dict

        Raises:
            httpx.HTTPError: If the request fails
        """
        # Filter out None, empty strings, and 0 values
        params = filter_params(params)
        seconds_since_last_call = (datetime.now() - self.last_call).total_seconds()
        if seconds_since_last_call < settings.nyt_rate_limit_seconds:
            await asyncio.sleep(
                settings.nyt_rate_limit_seconds - seconds_since_last_call
            )

        # Add API key to params
        params["api-key"] = self.api_key

        url = f"{settings.nyt_api_base_url}/{endpoint}"

        self.last_call = datetime.now()
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

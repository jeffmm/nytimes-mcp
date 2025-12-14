"""Tests for nyt_client.py HTTP client functionality."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from nytimes_mcp.nyt_client import NytClient, filter_params


class TestFilterParams:
    """Tests for filter_params function."""

    def test_filters_none_values(self):
        """Test that None values are filtered out."""
        params = {"key1": "value1", "key2": None, "key3": "value3"}
        result = filter_params(params)

        assert result == {"key1": "value1", "key3": "value3"}
        assert "key2" not in result

    def test_filters_empty_strings(self):
        """Test that empty strings are filtered out."""
        params = {"key1": "value1", "key2": "", "key3": "value3"}
        result = filter_params(params)

        assert result == {"key1": "value1", "key3": "value3"}
        assert "key2" not in result

    def test_filters_zero_values(self):
        """Test that 0 values are filtered out."""
        params = {"key1": "value1", "key2": 0, "key3": 42}
        result = filter_params(params)

        assert result == {"key1": "value1", "key3": 42}
        assert "key2" not in result

    def test_keeps_valid_values(self):
        """Test that valid values are kept."""
        params = {
            "string": "value",
            "number": 42,
            "negative": -1,
            "float": 3.14,
            "bool_true": True,
            "list": [1, 2, 3],
        }
        result = filter_params(params)

        # All should be kept
        assert "string" in result
        assert "number" in result
        assert "negative" in result
        assert "float" in result
        assert "bool_true" in result
        assert "list" in result

    def test_filters_false_value(self):
        """Test that False is filtered (since False == 0)."""
        params = {"bool_false": False, "other": "value"}
        result = filter_params(params)

        # False should be filtered out since False == 0 in Python
        assert "bool_false" not in result
        assert "other" in result

    def test_empty_dict(self):
        """Test with empty dictionary."""
        params = {}
        result = filter_params(params)

        assert result == {}

    def test_all_filtered(self):
        """Test when all values are filtered."""
        params = {"key1": None, "key2": "", "key3": 0}
        result = filter_params(params)

        assert result == {}


class TestNytClientInit:
    """Tests for NytClient initialization."""

    def test_client_initialization(self):
        """Test that client initializes correctly with settings."""
        client = NytClient()

        assert isinstance(client.client, httpx.AsyncClient)
        assert isinstance(client.api_key, str)
        assert len(client.api_key) > 0
        assert client.last_call == datetime.min


class TestNytClientMakeRequest:
    """Tests for NytClient.make_nyt_request method."""

    async def test_make_request_success(
        self, mock_httpx_response, sample_article_search_response
    ):
        """Test successful API request."""
        client = NytClient()

        # Mock the httpx client's get method
        mock_response = mock_httpx_response(sample_article_search_response)
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.make_nyt_request(
            "search/v2/articlesearch.json", {"q": "test"}
        )

        assert result == sample_article_search_response
        client.client.get.assert_called_once()

        # Verify the call arguments
        call_args = client.client.get.call_args
        assert "https://api.nytimes.com/svc/search/v2/articlesearch.json" in str(
            call_args
        )

    async def test_adds_api_key_to_params(self, mock_httpx_response):
        """Test that API key is added to request params."""
        client = NytClient()

        mock_response = mock_httpx_response({"status": "OK"})
        client.client.get = AsyncMock(return_value=mock_response)

        await client.make_nyt_request("test/endpoint.json", {"param": "value"})

        # Check that api-key was added to params
        call_args = client.client.get.call_args
        params = call_args.kwargs["params"]
        assert "api-key" in params
        assert isinstance(params["api-key"], str)
        assert len(params["api-key"]) > 0

    async def test_filters_params(self, mock_httpx_response):
        """Test that params are filtered before request."""
        client = NytClient()

        mock_response = mock_httpx_response({"status": "OK"})
        client.client.get = AsyncMock(return_value=mock_response)

        await client.make_nyt_request(
            "test/endpoint.json",
            {"valid": "value", "none_value": None, "empty": "", "zero": 0},
        )

        # Check that filtered params were used
        call_args = client.client.get.call_args
        params = call_args.kwargs["params"]
        assert "valid" in params
        assert "none_value" not in params
        assert "empty" not in params
        assert "zero" not in params

    async def test_constructs_correct_url(self, mock_httpx_response):
        """Test that URL is constructed correctly."""
        client = NytClient()

        mock_response = mock_httpx_response({"status": "OK"})
        client.client.get = AsyncMock(return_value=mock_response)

        await client.make_nyt_request("books/v3/lists/overview.json", {})

        call_args = client.client.get.call_args
        url = call_args.args[0]
        assert url == "https://api.nytimes.com/svc/books/v3/lists/overview.json"

    async def test_raises_on_http_error(self):
        """Test that HTTP errors are raised."""
        client = NytClient()

        # Mock a failed response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=Mock()
        )
        client.client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(httpx.HTTPStatusError):
            await client.make_nyt_request("test/endpoint.json", {})

    async def test_updates_last_call_timestamp(self, mock_httpx_response):
        """Test that last_call timestamp is updated."""
        client = NytClient()

        mock_response = mock_httpx_response({"status": "OK"})
        client.client.get = AsyncMock(return_value=mock_response)

        initial_last_call = client.last_call
        await client.make_nyt_request("test/endpoint.json", {})

        assert client.last_call > initial_last_call
        assert client.last_call <= datetime.now()

    @patch("nytimes_mcp.nyt_client.asyncio.sleep")
    async def test_rate_limiting(self, mock_sleep, mock_httpx_response):
        """Test that rate limiting works correctly."""
        from nytimes_mcp.config import settings

        client = NytClient()

        mock_response = mock_httpx_response({"status": "OK"})
        client.client.get = AsyncMock(return_value=mock_response)

        # Make first request
        await client.make_nyt_request("test/endpoint.json", {})
        assert mock_sleep.call_count == 0

        # Make second request immediately - should trigger rate limiting
        await client.make_nyt_request("test/endpoint.json", {})

        # Should have called sleep with approximately the rate limit seconds
        assert mock_sleep.call_count == 1
        sleep_duration = mock_sleep.call_args[0][0]
        assert sleep_duration > 0
        assert sleep_duration <= settings.nyt_rate_limit_seconds

    @patch("nytimes_mcp.nyt_client.asyncio.sleep")
    async def test_no_rate_limiting_after_delay(self, mock_sleep, mock_httpx_response):
        """Test that no rate limiting occurs after sufficient delay."""
        from nytimes_mcp.config import settings

        client = NytClient()

        mock_response = mock_httpx_response({"status": "OK"})
        client.client.get = AsyncMock(return_value=mock_response)

        # Make first request
        await client.make_nyt_request("test/endpoint.json", {})

        # Simulate time passing by setting last_call to past
        client.last_call = datetime.now() - timedelta(
            seconds=settings.nyt_rate_limit_seconds + 1
        )

        # Make second request - should not trigger rate limiting
        await client.make_nyt_request("test/endpoint.json", {})

        assert mock_sleep.call_count == 0

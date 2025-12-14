"""Shared fixtures for NYT MCP Server tests."""

import os
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from httpx import AsyncClient, Response


@pytest.fixture
def mock_api_key():
    """Provide a test API key."""
    return "test-api-key-12345"


@pytest.fixture
def sample_article_search_response() -> dict[str, Any]:
    """Sample response from NYT Article Search API."""
    return {
        "status": "OK",
        "copyright": "Copyright (c) 2024 The New York Times Company.",
        "response": {
            "docs": [
                {
                    "headline": {"main": "Test Article 1"},
                    "snippet": "This is a test snippet",
                    "web_url": "https://www.nytimes.com/test-article-1",
                    "pub_date": "2024-01-01T00:00:00+0000",
                },
                {
                    "headline": {"main": "Test Article 2"},
                    "snippet": "Another test snippet",
                    "web_url": "https://www.nytimes.com/test-article-2",
                    "pub_date": "2024-01-02T00:00:00+0000",
                },
            ],
            "meta": {"hits": 2, "offset": 0, "time": 10},
        },
    }


@pytest.fixture
def sample_news_wire_response() -> dict[str, Any]:
    """Sample response from NYT News Wire API."""
    return {
        "status": "OK",
        "copyright": "Copyright (c) 2024 The New York Times Company.",
        "results": [
            {
                "title": "Breaking News",
                "abstract": "This is breaking news",
                "url": "https://www.nytimes.com/breaking-news",
                "section": "World",
                "subsection": "",
                "published_date": "2024-01-01T12:00:00-05:00",
                "byline": "By Test Author",
            },
            {
                "title": "More News",
                "abstract": "More news abstract",
                "url": "https://www.nytimes.com/more-news",
                "section": "U.S.",
                "subsection": "Politics",
                "published_date": "2024-01-01T13:00:00-05:00",
                "byline": "By Another Author",
            },
        ],
    }


@pytest.fixture
def sample_most_popular_response() -> dict[str, Any]:
    """Sample response from NYT Most Popular API."""
    return {
        "status": "OK",
        "copyright": "Copyright (c) 2024 The New York Times Company.",
        "results": [
            {
                "title": "Popular Article",
                "abstract": "This is very popular",
                "url": "https://www.nytimes.com/popular",
                "published_date": "2024-01-01",
            },
        ],
    }


@pytest.fixture
def sample_archive_response() -> dict[str, Any]:
    """Sample response from NYT Archive API."""
    return {
        "status": "OK",
        "copyright": "Copyright (c) 2024 The New York Times Company.",
        "response": {
            "docs": [
                {
                    "headline": {"main": "Archive Article"},
                    "web_url": "https://www.nytimes.com/archive",
                }
            ]
        },
    }


@pytest.fixture
def sample_bestseller_response() -> dict[str, Any]:
    """Sample response from NYT Books API."""
    return {
        "status": "OK",
        "copyright": "Copyright (c) 2024 The New York Times Company.",
        "results": {
            "lists": [
                {
                    "list_name": "Hardcover Fiction",
                    "list_name_encoded": "hardcover-fiction",
                    "books": [
                        {
                            "title": "Test Book",
                            "author": "Test Author",
                            "rank": 1,
                        }
                    ],
                }
            ]
        },
    }


@pytest.fixture
def sample_section_list_response() -> dict[str, Any]:
    """Sample response from NYT Section List API."""
    return {
        "status": "OK",
        "results": [
            {"section": "world"},
            {"section": "business"},
            {"section": "technology"},
        ],
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient."""
    mock_client = AsyncMock(spec=AsyncClient)
    return mock_client


@pytest.fixture
def mock_httpx_response():
    """Factory for creating mock httpx Response objects."""

    def _create_response(json_data: dict[str, Any], status_code: int = 200):
        response = Mock(spec=Response)
        response.json.return_value = json_data
        response.status_code = status_code
        response.raise_for_status = Mock()
        return response

    return _create_response


@pytest.fixture(autouse=True)
def reset_module_client():
    """Reset the module-level client before each test."""
    import nytimes_mcp.tools

    nytimes_mcp.tools._nyt_client = None
    yield
    nytimes_mcp.tools._nyt_client = None


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch, mock_api_key):
    """Mock environment variables for all tests."""
    monkeypatch.setenv("NYT_API_KEY", mock_api_key)
    monkeypatch.setenv("NYT_API_BASE_URL", "https://api.nytimes.com/svc")
    monkeypatch.setenv("NYT_RATE_LIMIT_SECONDS", "12")

    # Reload settings after setting env var
    import nytimes_mcp.config

    nytimes_mcp.config.settings = nytimes_mcp.config.Settings(
        nyt_api_key=mock_api_key,
        nyt_api_base_url="https://api.nytimes.com/svc",
        nyt_rate_limit_seconds=12,
    )
    yield
    # Reset settings after test
    nytimes_mcp.config.settings = nytimes_mcp.config.Settings.model_validate({})

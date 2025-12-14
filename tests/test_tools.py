"""Tests for tools.py MCP tool implementations."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from nytimes_mcp import tools
from nytimes_mcp.nyt_client import NytClient


class TestGetClient:
    """Tests for get_client function."""

    def test_creates_client_on_first_call(self):
        """Test that client is created on first call."""
        # Client should be None initially (reset by fixture)
        assert tools._nyt_client is None

        client = tools.get_client()

        assert isinstance(client, NytClient)
        assert tools._nyt_client is client

    def test_returns_same_client_on_subsequent_calls(self):
        """Test that same client is returned on subsequent calls."""
        client1 = tools.get_client()
        client2 = tools.get_client()

        assert client1 is client2


class TestSearchArticles:
    """Tests for search_articles tool."""

    async def test_search_articles_basic(
        self, mock_httpx_response, sample_article_search_response
    ):
        """Test basic article search."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_article_search_response,
        ) as mock_request:
            result = await tools.search_articles("test query")

            # Verify request was made with correct parameters
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "search/v2/articlesearch.json"
            params = call_args[0][1]
            assert params["q"] == "test query"
            assert params["sort"] == "best"

            # Verify response is formatted
            assert "articles" in result
            assert "total_hits" in result

    async def test_search_articles_with_date_range(
        self, sample_article_search_response
    ):
        """Test article search with date range."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_article_search_response,
        ) as mock_request:
            result = await tools.search_articles(
                "test", begin_date="20240101", end_date="20240131"
            )

            params = mock_request.call_args[0][1]
            assert params["begin_date"] == "20240101"
            assert params["end_date"] == "20240131"

    async def test_search_articles_invalid_begin_date(self):
        """Test that invalid begin_date raises ValueError."""
        with pytest.raises(ValueError, match="begin_date must be in YYYYMMDD format"):
            await tools.search_articles("test", begin_date="2024-01-01")

    async def test_search_articles_invalid_end_date(self):
        """Test that invalid end_date raises ValueError."""
        with pytest.raises(ValueError, match="end_date must be in YYYYMMDD format"):
            await tools.search_articles("test", end_date="2024-01-31")

    async def test_search_articles_with_page(self, sample_article_search_response):
        """Test article search with pagination."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_article_search_response,
        ) as mock_request:
            result = await tools.search_articles("test", page=5)

            params = mock_request.call_args[0][1]
            assert params["page"] == "5"

    async def test_search_articles_page_zero_excluded(
        self, sample_article_search_response
    ):
        """Test that page=0 is not included in params."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_article_search_response,
        ) as mock_request:
            result = await tools.search_articles("test", page=0)

            params = mock_request.call_args[0][1]
            assert "page" not in params

    async def test_search_articles_invalid_page(self):
        """Test that invalid page number raises ValueError."""
        with pytest.raises(ValueError, match="Page number must be between 0 and 100"):
            await tools.search_articles("test", page=101)

    async def test_search_articles_different_sort_orders(
        self, sample_article_search_response
    ):
        """Test article search with different sort orders."""
        for sort_order in ["best", "newest", "oldest", "relevance"]:
            with patch.object(
                NytClient,
                "make_nyt_request",
                new_callable=AsyncMock,
                return_value=sample_article_search_response,
            ) as mock_request:
                result = await tools.search_articles("test", sort=sort_order)

                params = mock_request.call_args[0][1]
                assert params["sort"] == sort_order

    async def test_search_articles_strips_query(self, sample_article_search_response):
        """Test that query is stripped of whitespace."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_article_search_response,
        ) as mock_request:
            result = await tools.search_articles("  test query  ")

            params = mock_request.call_args[0][1]
            assert params["q"] == "test query"


class TestGetNewsSections:
    """Tests for get_news_sections tool."""

    async def test_get_news_sections(self, sample_section_list_response):
        """Test getting news sections."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_section_list_response,
        ) as mock_request:
            result = await tools.get_news_sections()

            mock_request.assert_called_once_with(
                "news/v3/content/section-list.json", {}
            )
            assert result == ["world", "business", "technology"]

    async def test_get_news_sections_empty_results(self):
        """Test getting news sections with empty results."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value={"results": []},
        ):
            result = await tools.get_news_sections()

            assert result == []


class TestGetNewsWire:
    """Tests for get_news_wire tool."""

    async def test_get_news_wire_defaults(self, sample_news_wire_response):
        """Test news wire with default parameters."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_news_wire_response,
        ) as mock_request:
            result = await tools.get_news_wire()

            call_args = mock_request.call_args
            assert call_args[0][0] == "news/v3/content/nyt/all.json"
            params = call_args[0][1]
            assert params["limit"] == 20
            assert params["offset"] == 0

            assert "news_items" in result
            assert "num_results" in result

    async def test_get_news_wire_with_params(self, sample_news_wire_response):
        """Test news wire with custom parameters."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_news_wire_response,
        ) as mock_request:
            result = await tools.get_news_wire(
                limit=50, offset=10, source="inyt", section="world"
            )

            call_args = mock_request.call_args
            assert call_args[0][0] == "news/v3/content/inyt/world.json"
            params = call_args[0][1]
            assert params["limit"] == 50
            assert params["offset"] == 10


class TestGetMostPopular:
    """Tests for get_most_popular tool."""

    async def test_get_most_popular_defaults(self, sample_most_popular_response):
        """Test most popular with default parameters."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_most_popular_response,
        ) as mock_request:
            result = await tools.get_most_popular()

            mock_request.assert_called_once_with(
                "mostpopular/v2/viewed/1.json",
                {},
            )

            assert "articles" in result
            assert "num_results" in result

    async def test_get_most_popular_different_types(self, sample_most_popular_response):
        """Test most popular with different popularity types."""
        for pop_type in ["viewed", "shared", "emailed"]:
            with patch.object(
                NytClient,
                "make_nyt_request",
                new_callable=AsyncMock,
                return_value=sample_most_popular_response,
            ) as mock_request:
                result = await tools.get_most_popular(popularity_type=pop_type)

                endpoint = mock_request.call_args[0][0]
                assert pop_type in endpoint

    async def test_get_most_popular_different_periods(
        self, sample_most_popular_response
    ):
        """Test most popular with different time periods."""
        for period in ["1", "7", "30"]:
            with patch.object(
                NytClient,
                "make_nyt_request",
                new_callable=AsyncMock,
                return_value=sample_most_popular_response,
            ) as mock_request:
                result = await tools.get_most_popular(time_period=period)

                endpoint = mock_request.call_args[0][0]
                assert endpoint.endswith(f"/{period}.json")


class TestGetArchive:
    """Tests for get_archive tool."""

    async def test_get_archive_defaults(self, sample_archive_response):
        """Test archive with default parameters (current year/month)."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_archive_response,
        ) as mock_request:
            result = await tools.get_archive()

            now = datetime.now()
            expected_endpoint = f"archive/v1/{now.year}/{now.month}.json"
            mock_request.assert_called_once_with(expected_endpoint, {})

            # Should return raw response (not formatted)
            assert result == sample_archive_response

    async def test_get_archive_with_params(self, sample_archive_response):
        """Test archive with specific year and month."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_archive_response,
        ) as mock_request:
            result = await tools.get_archive(year=2024, month=6)

            mock_request.assert_called_once_with("archive/v1/2024/6.json", {})


class TestGetBestsellerListNames:
    """Tests for get_bestseller_list_names tool."""

    async def test_get_bestseller_list_names(self, sample_bestseller_response):
        """Test getting bestseller list names."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_bestseller_response,
        ) as mock_request:
            result = await tools.get_bestseller_list_names()

            mock_request.assert_called_once_with("books/v3/lists/overview.json", {})
            assert result == ["hardcover-fiction"]


class TestGetBestsellerListsOverview:
    """Tests for get_bestseller_lists_overview tool."""

    async def test_get_bestseller_lists_overview(self, sample_bestseller_response):
        """Test getting bestseller lists overview."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_bestseller_response,
        ) as mock_request:
            result = await tools.get_bestseller_lists_overview()

            mock_request.assert_called_once_with("books/v3/lists/overview.json", {})
            # Should return raw response (not formatted)
            assert result == sample_bestseller_response


class TestGetBestsellerList:
    """Tests for get_bestseller_list tool."""

    async def test_get_bestseller_list_defaults(self, sample_bestseller_response):
        """Test bestseller list with default parameters."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_bestseller_response,
        ) as mock_request:
            result = await tools.get_bestseller_list()

            call_args = mock_request.call_args
            assert call_args[0][0] == "books/v3/lists/current/hardcover-fiction.json"
            params = call_args[0][1]
            assert params["offset"] == 0

            # Should return raw response (not formatted)
            assert result == sample_bestseller_response

    async def test_get_bestseller_list_with_params(self, sample_bestseller_response):
        """Test bestseller list with custom parameters."""
        with patch.object(
            NytClient,
            "make_nyt_request",
            new_callable=AsyncMock,
            return_value=sample_bestseller_response,
        ) as mock_request:
            result = await tools.get_bestseller_list(
                list="paperback-nonfiction", offset=20
            )

            call_args = mock_request.call_args
            assert call_args[0][0] == "books/v3/lists/current/paperback-nonfiction.json"
            params = call_args[0][1]
            assert params["offset"] == 20


class TestCleanupHttpClient:
    """Tests for cleanup_http_client function."""

    async def test_cleanup_http_client(self):
        """Test cleaning up the HTTP client."""
        # Create a client first
        client = tools.get_client()
        assert tools._nyt_client is not None

        # Mock the aclose method
        client.client.aclose = AsyncMock()

        # Clean up
        await tools.cleanup_http_client()

        # Verify cleanup
        client.client.aclose.assert_called_once()
        assert tools._nyt_client is None

    async def test_cleanup_when_no_client(self):
        """Test cleanup when no client exists."""
        # Ensure no client exists
        assert tools._nyt_client is None

        # Should not raise an error
        await tools.cleanup_http_client()

        assert tools._nyt_client is None

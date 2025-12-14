"""MCP tool definitions for NYT API endpoints."""

from datetime import datetime
from typing import Literal

from nytimes_mcp.nyt_client import NytClient
from nytimes_mcp.utils import (
    format_articles_response,
    format_news_items_response,
    format_popular_response,
)

# Module-level client
_nyt_client: NytClient | None = None


def get_client() -> NytClient:
    """Get or create the shared HTTP client."""
    global _nyt_client
    if _nyt_client is None:
        _nyt_client = NytClient()
    return _nyt_client


type NewsSource = Literal["nyt", "inyt", "all"]
type SortOrder = Literal["best", "newest", "oldest", "relevance"]
type PopularityType = Literal["viewed", "shared", "emailed"]
type PopularityPeriod = Literal["1", "7", "30"]


async def search_articles(
    query: str,
    sort: SortOrder = "best",
    begin_date: str | None = None,
    end_date: str | None = None,
    page: int | None = None,
) -> dict:
    """
    Search New York Times articles by query, date range, and other criteria.

    Args:
        query: Search query string
        sort: Sort order - "best", "newest", "oldest", or "relevance" (default: "best")
        begin_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)
        page: Page number for pagination (10 articles per page), 0-indexed, max=100 (optional)

    Returns:
        Formatted response with articles array containing headline, snippet, web_url, and pub_date
    """
    params = {
        "q": query.strip(),
        "sort": sort,
    }

    # Add optional date parameters only if specified
    if begin_date and len(begin_date) == 8:
        params["begin_date"] = begin_date
    elif begin_date:
        raise ValueError("begin_date must be in YYYYMMDD format.")
    if end_date and len(end_date) == 8:
        params["end_date"] = end_date
    elif end_date:
        raise ValueError("end_date must be in YYYYMMDD format.")

    # Only add page if it's greater than 0
    if page and page > 0 and page <= 100:
        params["page"] = str(page)
    elif page and page != 0:
        raise ValueError("Page number must be between 0 and 100.")

    client = get_client()
    response = await client.make_nyt_request("search/v2/articlesearch.json", params)

    return format_articles_response(response)


async def get_news_sections() -> list[str]:
    """
    Get the list of available news sections from the NYT news wire.

    Returns:
        List of section names as strings
    """
    client = get_client()
    response = await client.make_nyt_request("news/v3/content/section-list.json", {})

    sections = response.get("results", [])
    return [section.get("section") for section in sections if "section" in section]


async def get_news_wire(
    limit: int = 20,
    offset: int = 0,
    source: NewsSource = "nyt",
    section: str = "all",
) -> dict:
    """
    Get the latest news items from the NYT news wire (real-time news feed).

    Args:
        limit: Number of items to return (default: 20)
        offset: Pagination offset (default: 0)
        source: News source - "nyt", "inyt", or "all" (default: "nyt")
        section: News section (e.g., "all", "world", "business") (default:
            "all"). To see the latest list of sections available, refer to the
            get_news_sections tool.

    Returns:
        Formatted response with news_items array containing title, abstract, url, section,
        subsection, published_date, and byline
    """
    params = {
        "limit": limit,
        "offset": offset,
    }

    client = get_client()
    response = await client.make_nyt_request(
        f"news/v3/content/{source}/{section}.json", params
    )

    return format_news_items_response(response)


async def get_most_popular(
    popularity_type: PopularityType = "viewed",
    time_period: PopularityPeriod = "1",
) -> dict:
    """
    Get the most popular New York Times articles.

    Args:
        popularity_type: Type of popularity - "viewed", "shared", or "emailed" (default: "viewed")
        time_period: Time period in days - "1", "7", or "30" (default: "1")

    Returns:
        Formatted response with articles array containing title, abstract, url, and published_date
    """
    client = get_client()
    response = await client.make_nyt_request(
        f"mostpopular/v2/{popularity_type}/{time_period}.json",
        {},
    )

    return format_popular_response(response)


async def get_archive(year: int | None = None, month: int | None = None) -> dict:
    """
    Get New York Times articles from a specific month and year archive.

    Args:
        year: Year (default: current year)
        month: Month 1-12 (default: current month)

    Returns:
        Full NYT archive API response (unformatted)
    """
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    client = get_client()
    response = await client.make_nyt_request(f"archive/v1/{year}/{month}.json", {})

    # Return raw response (no formatting for archive)
    return response


async def get_bestseller_list_names() -> list[str]:
    """
    Get overview of New York Times bestseller lists.

    Returns:
        Full NYT Books API response (unformatted)
    """
    client = get_client()
    response = await client.make_nyt_request("books/v3/lists/overview.json", {})

    # Return raw response (no formatting for books)
    return [r["list_name_encoded"] for r in response["results"]["lists"]]


async def get_bestseller_lists_overview() -> dict:
    """
    Get overview of New York Times bestseller lists.

    Returns:
        Full NYT Books API response (unformatted)
    """
    client = get_client()
    response = await client.make_nyt_request("books/v3/lists/overview.json", {})

    # Return raw response (no formatting for books)
    return response


async def get_bestseller_list(list: str = "hardcover-fiction", offset: int = 0) -> dict:
    """
    Get New York Times bestseller lists.

    Args:
        list: List name (e.g., "hardcover-fiction", "hardcover-nonfiction", "paperback-nonfiction")
              Default is "hardcover-fiction"
        offset: Pagination offset (default: 0)

    Returns:
        Full NYT Books API response (unformatted)
    """
    params = {"offset": offset}

    client = get_client()
    response = await client.make_nyt_request(
        f"books/v3/lists/current/{list}.json",
        params,
    )

    # Return raw response (no formatting for books)
    return response


async def cleanup_http_client():
    """Close the shared HTTP client."""
    global _nyt_client
    if _nyt_client is not None:
        await _nyt_client.client.aclose()
        _nyt_client = None

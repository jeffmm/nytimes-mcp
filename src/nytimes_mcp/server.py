"""NYT MCP Server - FastMCP-based server for New York Times API."""

from fastmcp import FastMCP

from nytimes_mcp import resources, tools

# Initialize FastMCP server
mcp = FastMCP("nytimes-mcp", dependencies=["httpx", "pydantic", "python-dotenv"])


# Register all tools
@mcp.tool()
async def search_articles(
    query: str,
    sort: tools.SortOrder = "best",
    begin_date: str | None = None,
    end_date: str | None = None,
    page: int | None = None,
) -> dict:
    """
    Search New York Times articles by query, date range, and other criteria.

    Args:
        query: Search query string
        sort: Sort order - "newest" or "oldest" (default: "newest")
        begin_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)
        page: Page number for pagination, 0-indexed (optional)

    Returns:
        Formatted response with articles array containing headline, snippet, web_url, and pub_date
    """
    return await tools.search_articles(query, sort, begin_date, end_date, page)


@mcp.tool()
async def get_news_wire(
    limit: int = 20,
    offset: int = 0,
    source: tools.NewsSource = "nyt",
    section: str = "all",
) -> dict:
    """
    Get the latest news items from the NYT news wire (real-time news feed).

    Args:
        limit: Number of items to return (default: 20)
        offset: Pagination offset (default: 0)
        source: News source - "nyt" or "inyt" (default: "nyt")

    Returns:
        Formatted response with news_items array containing title, abstract, url, section,
        subsection, published_date, and byline
    """
    return await tools.get_news_wire(limit, offset, source, section)


@mcp.tool()
async def get_most_popular(
    popularity_type: tools.PopularityType = "viewed",
    time_period: tools.PopularityPeriod = "1",
) -> dict:
    """
    Get the most popular New York Times articles.

    Args:
        type: Type of popularity - "viewed", "shared", or "emailed" (default: "viewed")
        time_period: Time period in days - "1", "7", or "30" (default: "1")
              Use the 'nyt://reference/popular-types' resource for available options.

    Returns:
        Formatted response with articles array containing title, abstract, url, and published_date
    """
    return await tools.get_most_popular(popularity_type, time_period)


@mcp.tool()
async def get_archive(year: int | None = None, month: int | None = None) -> dict:
    """
    Get New York Times articles from a specific month and year archive.

    Args:
        year: Year (default: current year)
        month: Month 1-12 (default: current month)

    Returns:
        Full NYT archive API response (unformatted)
    """
    return await tools.get_archive(year, month)


@mcp.tool()
async def get_bestseller_list(list: str = "hardcover-fiction", offset: int = 0) -> dict:
    """
    Get New York Times bestseller lists.

    Args:
        list: List name (e.g., "hardcover-fiction", "hardcover-nonfiction", "paperback-nonfiction")
              Default is "hardcover-fiction". Use the 'nyt://reference/bestseller-lists' resource
              for available list names.
        offset: Pagination offset (default: 0)

    Returns:
        Full NYT Books API response (unformatted)
    """
    return await tools.get_bestseller_list(list, offset)


# Register all resources
@mcp.resource("nyt://reference/sections")
def list_sections() -> dict:
    """Available sections for the get_top_stories tool."""
    return resources.get_available_sections()


@mcp.resource("nyt://reference/bestseller-lists")
def list_bestseller_lists() -> dict:
    """Available bestseller list names for the get_bestseller_list tool."""
    return resources.get_bestseller_lists()


@mcp.resource("nyt://reference/api-limits")
def list_api_limits() -> dict:
    """NYT API rate limits and usage information."""
    return resources.get_api_limits()


def main():
    """Main entry point for the NYT MCP server."""
    import asyncio

    # Cleanup handler for HTTP client
    async def cleanup():
        await tools.cleanup_http_client()

    try:
        mcp.run()
    finally:
        # Run cleanup
        asyncio.run(cleanup())


if __name__ == "__main__":
    main()

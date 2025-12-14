"""MCP resource definitions for NYT API reference data."""


def get_available_sections() -> dict:
    """
    Get available sections for the top_stories endpoint.

    Returns:
        Dict with sections array
    """
    return {
        "sections": [
            "admin",
            "all",
            "arts",
            "automobiles",
            "books",
            "briefing",
            "business",
            "climate",
            "corrections",
            "education",
            "en español",
            "fashion",
            "food",
            "gameplay",
            "guide",
            "health",
            "home & garden",
            "home page",
            "job market",
            "the learning network",
            "lens",
            "magazine",
            "movies",
            "multimedia/photos",
            "new york",
            "obituaries",
            "opinion",
            "parenting",
            "podcasts",
            "reader center",
            "real estate",
            "smarter living",
            "science",
            "sports",
            "style",
            "sunday review",
            "t brand",
            "t magazine",
            "technology",
            "theater",
            "times insider",
            "today’s paper",
            "travel",
            "u.s.",
            "universal",
            "the upshot",
            "video",
            "the weekly",
            "well",
            "world",
            "your money",
        ],
        "description": "Available sections for the get_news_wire tool",
    }


def get_bestseller_lists() -> dict:
    """
    Get available bestseller list names for the books endpoint.

    Returns:
        Dict with lists array
    """
    return {
        "lists": [
            "combined-print-and-e-book-fiction",
            "combined-print-and-e-book-nonfiction",
            "hardcover-fiction",
            "hardcover-nonfiction",
            "trade-fiction-paperback",
            "paperback-nonfiction",
            "advice-how-to-and-miscellaneous",
            "childrens-middle-grade-hardcover",
            "picture-books",
            "series-books",
            "young-adult-hardcover",
            "audio-fiction",
            "audio-nonfiction",
            "business-books",
            "graphic-books-and-manga",
            "mass-market-monthly",
            "middle-grade-paperback-monthly",
            "young-adult-paperback-monthly",
        ],
        "description": "Available bestseller list names for the get_bestseller_list tool",
        "note": "List names use hyphens instead of spaces. Visit developer.nytimes.com for the complete list.",
    }


def get_api_limits() -> dict:
    """
    Get NYT API rate limits and usage information.

    Returns:
        Dict with rate limit information
    """
    return {
        "rate_limits": {
            "requests_per_minute": 5,
            "requests_per_day": 500,
        },
        "description": "NYT API rate limits for standard API keys",
        "note": "These are approximate limits. Refer to https://developer.nytimes.com for current rate limits and usage guidelines.",
        "recommendations": [
            "Implement caching for frequently accessed data",
            "Use pagination parameters (offset, limit) to reduce request volume",
            "Monitor API responses for rate limit headers",
        ],
    }

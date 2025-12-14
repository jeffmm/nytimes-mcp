"""Response formatting utilities for NYT API responses."""

from typing import Any


def format_articles_response(response: dict[str, Any]) -> dict[str, Any]:
    """
    Format article search response to extract essential fields.

    Args:
        response: Raw NYT article search API response

    Returns:
        Formatted response with articles array and total_hits
    """
    if "response" in response and "docs" in response["response"]:
        return {
            "articles": [
                {
                    "headline": doc.get("headline", {}).get("main", ""),
                    "snippet": doc.get("snippet", ""),
                    "web_url": doc.get("web_url", ""),
                    "pub_date": doc.get("pub_date", ""),
                }
                for doc in response["response"]["docs"]
            ],
            "total_hits": response["response"].get("meta", {}).get("hits", 0),
        }
    return response


def format_news_items_response(response: dict[str, Any]) -> dict[str, Any]:
    """
    Format times wire (news feed) response to extract essential fields.

    Args:
        response: Raw NYT times wire API response

    Returns:
        Formatted response with news_items array and num_results
    """
    if "results" in response:
        return {
            "news_items": [
                {
                    "title": item.get("title", ""),
                    "abstract": item.get("abstract", ""),
                    "url": item.get("url", ""),
                    "section": item.get("section", ""),
                    "subsection": item.get("subsection", ""),
                    "published_date": item.get("published_date", ""),
                    "byline": item.get("byline", ""),
                }
                for item in response["results"]
            ],
            "num_results": len(response["results"]),
        }
    return response


def format_popular_response(response: dict[str, Any]) -> dict[str, Any]:
    """
    Format most popular response to extract essential fields.

    Args:
        response: Raw NYT most popular API response

    Returns:
        Formatted response with articles array and num_results
    """
    if "results" in response:
        return {
            "articles": [
                {
                    "title": article.get("title", ""),
                    "abstract": article.get("abstract", ""),
                    "url": article.get("url", ""),
                    "published_date": article.get("published_date", ""),
                }
                for article in response["results"]
            ],
            "num_results": len(response["results"]),
        }
    return response

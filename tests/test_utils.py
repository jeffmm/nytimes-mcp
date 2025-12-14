"""Tests for utils.py response formatting functions."""

import pytest

from nytimes_mcp.utils import (
    format_articles_response,
    format_news_items_response,
    format_popular_response,
)


class TestFormatArticlesResponse:
    """Tests for format_articles_response."""

    def test_format_valid_response(self, sample_article_search_response):
        """Test formatting a valid article search response."""
        result = format_articles_response(sample_article_search_response)

        assert "articles" in result
        assert "total_hits" in result
        assert len(result["articles"]) == 2
        assert result["total_hits"] == 2

        # Check first article structure
        article = result["articles"][0]
        assert article["headline"] == "Test Article 1"
        assert article["snippet"] == "This is a test snippet"
        assert article["web_url"] == "https://www.nytimes.com/test-article-1"
        assert article["pub_date"] == "2024-01-01T00:00:00+0000"

    def test_format_empty_docs(self):
        """Test formatting response with empty docs."""
        response = {"response": {"docs": [], "meta": {"hits": 0}}}
        result = format_articles_response(response)

        assert result["articles"] == []
        assert result["total_hits"] == 0

    def test_format_missing_fields(self):
        """Test formatting response with missing optional fields."""
        response = {
            "response": {
                "docs": [
                    {
                        "headline": {"main": "Title Only"},
                        # Missing snippet, web_url, pub_date
                    }
                ],
                "meta": {"hits": 1},
            }
        }
        result = format_articles_response(response)

        assert len(result["articles"]) == 1
        article = result["articles"][0]
        assert article["headline"] == "Title Only"
        assert article["snippet"] == ""
        assert article["web_url"] == ""
        assert article["pub_date"] == ""

    def test_format_invalid_response_structure(self):
        """Test formatting response with invalid structure."""
        response = {"invalid": "structure"}
        result = format_articles_response(response)

        # Should return original response if structure is invalid
        assert result == response

    def test_format_missing_meta(self):
        """Test formatting response with missing meta field."""
        response = {"response": {"docs": [{"headline": {"main": "Test"}}]}}
        result = format_articles_response(response)

        assert len(result["articles"]) == 1
        assert result["total_hits"] == 0  # Default when meta is missing


class TestFormatNewsItemsResponse:
    """Tests for format_news_items_response."""

    def test_format_valid_response(self, sample_news_wire_response):
        """Test formatting a valid news wire response."""
        result = format_news_items_response(sample_news_wire_response)

        assert "news_items" in result
        assert "num_results" in result
        assert len(result["news_items"]) == 2
        assert result["num_results"] == 2

        # Check first news item structure
        item = result["news_items"][0]
        assert item["title"] == "Breaking News"
        assert item["abstract"] == "This is breaking news"
        assert item["url"] == "https://www.nytimes.com/breaking-news"
        assert item["section"] == "World"
        assert item["subsection"] == ""
        assert item["published_date"] == "2024-01-01T12:00:00-05:00"
        assert item["byline"] == "By Test Author"

    def test_format_empty_results(self):
        """Test formatting response with empty results."""
        response = {"results": []}
        result = format_news_items_response(response)

        assert result["news_items"] == []
        assert result["num_results"] == 0

    def test_format_missing_fields(self):
        """Test formatting response with missing optional fields."""
        response = {
            "results": [
                {
                    "title": "Title Only",
                    # Missing other fields
                }
            ]
        }
        result = format_news_items_response(response)

        assert len(result["news_items"]) == 1
        item = result["news_items"][0]
        assert item["title"] == "Title Only"
        assert item["abstract"] == ""
        assert item["url"] == ""
        assert item["section"] == ""
        assert item["subsection"] == ""
        assert item["published_date"] == ""
        assert item["byline"] == ""

    def test_format_invalid_response_structure(self):
        """Test formatting response with invalid structure."""
        response = {"invalid": "structure"}
        result = format_news_items_response(response)

        # Should return original response if structure is invalid
        assert result == response


class TestFormatPopularResponse:
    """Tests for format_popular_response."""

    def test_format_valid_response(self, sample_most_popular_response):
        """Test formatting a valid most popular response."""
        result = format_popular_response(sample_most_popular_response)

        assert "articles" in result
        assert "num_results" in result
        assert len(result["articles"]) == 1
        assert result["num_results"] == 1

        # Check article structure
        article = result["articles"][0]
        assert article["title"] == "Popular Article"
        assert article["abstract"] == "This is very popular"
        assert article["url"] == "https://www.nytimes.com/popular"
        assert article["published_date"] == "2024-01-01"

    def test_format_empty_results(self):
        """Test formatting response with empty results."""
        response = {"results": []}
        result = format_popular_response(response)

        assert result["articles"] == []
        assert result["num_results"] == 0

    def test_format_missing_fields(self):
        """Test formatting response with missing optional fields."""
        response = {
            "results": [
                {
                    "title": "Title Only",
                    # Missing other fields
                }
            ]
        }
        result = format_popular_response(response)

        assert len(result["articles"]) == 1
        article = result["articles"][0]
        assert article["title"] == "Title Only"
        assert article["abstract"] == ""
        assert article["url"] == ""
        assert article["published_date"] == ""

    def test_format_invalid_response_structure(self):
        """Test formatting response with invalid structure."""
        response = {"invalid": "structure"}
        result = format_popular_response(response)

        # Should return original response if structure is invalid
        assert result == response

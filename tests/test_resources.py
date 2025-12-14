"""Tests for resources.py MCP resource definitions."""

import pytest

from nytimes_mcp.resources import (
    get_api_limits,
    get_available_sections,
    get_bestseller_lists,
)


class TestGetAvailableSections:
    """Tests for get_available_sections."""

    def test_returns_dict_with_sections(self):
        """Test that function returns a dict with sections array."""
        result = get_available_sections()

        assert isinstance(result, dict)
        assert "sections" in result
        assert "description" in result
        assert isinstance(result["sections"], list)

    def test_contains_expected_sections(self):
        """Test that result contains expected sections."""
        result = get_available_sections()

        sections = result["sections"]
        assert "all" in sections
        assert "world" in sections
        assert "business" in sections
        assert "technology" in sections
        assert "sports" in sections

    def test_sections_are_strings(self):
        """Test that all sections are strings."""
        result = get_available_sections()

        sections = result["sections"]
        assert all(isinstance(section, str) for section in sections)

    def test_has_description(self):
        """Test that result has a description field."""
        result = get_available_sections()

        assert "description" in result
        assert isinstance(result["description"], str)
        assert len(result["description"]) > 0


class TestGetBestsellerLists:
    """Tests for get_bestseller_lists."""

    def test_returns_dict_with_lists(self):
        """Test that function returns a dict with lists array."""
        result = get_bestseller_lists()

        assert isinstance(result, dict)
        assert "lists" in result
        assert "description" in result
        assert "note" in result
        assert isinstance(result["lists"], list)

    def test_contains_expected_lists(self):
        """Test that result contains expected bestseller lists."""
        result = get_bestseller_lists()

        lists = result["lists"]
        assert "hardcover-fiction" in lists
        assert "hardcover-nonfiction" in lists
        assert "paperback-nonfiction" in lists
        assert "combined-print-and-e-book-fiction" in lists

    def test_lists_use_hyphens(self):
        """Test that list names use hyphens instead of spaces."""
        result = get_bestseller_lists()

        lists = result["lists"]
        # All list names should use hyphens
        assert all("-" in list_name or list_name.isalpha() for list_name in lists)
        # No list names should have spaces
        assert all(" " not in list_name for list_name in lists)

    def test_lists_are_strings(self):
        """Test that all list names are strings."""
        result = get_bestseller_lists()

        lists = result["lists"]
        assert all(isinstance(list_name, str) for list_name in lists)

    def test_has_description_and_note(self):
        """Test that result has description and note fields."""
        result = get_bestseller_lists()

        assert "description" in result
        assert isinstance(result["description"], str)
        assert len(result["description"]) > 0

        assert "note" in result
        assert isinstance(result["note"], str)
        assert len(result["note"]) > 0


class TestGetApiLimits:
    """Tests for get_api_limits."""

    def test_returns_dict_with_rate_limits(self):
        """Test that function returns a dict with rate_limits."""
        result = get_api_limits()

        assert isinstance(result, dict)
        assert "rate_limits" in result
        assert "description" in result
        assert "note" in result
        assert "recommendations" in result

    def test_rate_limits_structure(self):
        """Test the structure of rate_limits."""
        result = get_api_limits()

        rate_limits = result["rate_limits"]
        assert isinstance(rate_limits, dict)
        assert "requests_per_minute" in rate_limits
        assert "requests_per_day" in rate_limits

    def test_rate_limit_values(self):
        """Test that rate limit values are correct."""
        result = get_api_limits()

        rate_limits = result["rate_limits"]
        assert rate_limits["requests_per_minute"] == 5
        assert rate_limits["requests_per_day"] == 500

    def test_has_recommendations(self):
        """Test that result has recommendations array."""
        result = get_api_limits()

        recommendations = result["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)

    def test_recommendations_content(self):
        """Test that recommendations contain useful information."""
        result = get_api_limits()

        recommendations = result["recommendations"]
        # Join all recommendations to check for key concepts
        all_recs = " ".join(recommendations).lower()
        assert any(
            word in all_recs for word in ["caching", "cache", "pagination", "limit"]
        )

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastMCP-based Model Context Protocol (MCP) server that provides access to the New York Times APIs. The server exposes 5 tools (one per NYT API endpoint) and 3 reference resources to MCP clients like Claude Desktop.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Install as editable package
uv tool install .
```

### Running the Server
```bash
# Development mode with MCP Inspector UI (interactive testing)
uv run fastmcp dev src/nytimes_mcp/server.py:mcp

# Production mode (for use with MCP clients)
uvx nytimes-mcp

# Alternative production mode
fastmcp run src/nytimes_mcp/server.py:mcp
```

### Testing
```bash
# Run tests
uv run pytest
```

### Environment Variables
Required environment variable: `NYT_API_KEY`
- Set in `.env` file: `NYT_API_KEY=your_api_key_here`
- Or export: `export NYT_API_KEY=your_api_key_here`
- Get API keys at: https://developer.nytimes.com/

## Architecture

### Core Components

**server.py** - FastMCP server initialization and tool/resource registration
- Initializes FastMCP instance with dependencies
- Loads environment variables and validates NYT_API_KEY
- Registers all MCP tools (5 total) and resources (3 total)
- Each `@mcp.tool()` decorator wraps a corresponding function from `tools.py`
- Each `@mcp.resource()` decorator wraps a corresponding function from `resources.py`
- Main entry point handles cleanup of HTTP client on shutdown

**tools.py** - NYT API tool implementations
- Defines type aliases for Literal types (NewsSource, SortOrder, PopularityType, PopularityPeriod)
- Implements 5 primary tools: `search_articles`, `get_news_wire`, `get_most_popular`, `get_archive`, `get_bestseller_list`
- Also provides helper functions: `get_news_sections`, `get_bestseller_list_names`, `get_bestseller_lists_overview`
- Uses module-level singleton `_nyt_client` instance for HTTP connection pooling
- Calls formatting utilities from `utils.py` for most endpoints (archive and bestseller return raw responses)
- Provides `cleanup_http_client()` for proper resource cleanup

**nyt_client.py** - HTTP client for NYT API requests
- `NytClient` class wraps httpx.AsyncClient with NYT-specific logic
- Implements rate limiting: tracks `last_call` timestamp and sleeps if needed (see config.py for rate limit)
- `filter_params()` removes None, empty strings, and 0 values to keep requests minimal
- `make_nyt_request()` adds API key, enforces rate limits, and handles errors
- Uses settings from `config.py` for base URL and rate limit configuration

**utils.py** - Response formatting utilities
- `format_articles_response()` - Extracts headline, snippet, web_url, pub_date from article search
- `format_news_items_response()` - Extracts title, abstract, url, section, etc. from news wire
- `format_popular_response()` - Extracts title, abstract, url, published_date from most popular
- All formatters return simplified dict structures with only essential fields

**resources.py** - MCP resource definitions (static reference data)
- `get_available_sections()` - Returns list of valid sections for news wire
- `get_bestseller_lists()` - Returns list of valid bestseller list names
- `get_api_limits()` - Returns NYT API rate limit information (5 req/min, 500 req/day)

**config.py** - Configuration management
- Uses Pydantic Settings with BaseSettings for environment variable management
- Loads from `.env` file automatically
- `nyt_api_key`: Required API key
- `nyt_api_base_url`: Base URL for NYT API (default: "https://api.nytimes.com/svc")
- `nyt_rate_limit_seconds`: Minimum seconds between requests (default: 12, which gives 5 req/min)

### Important Architectural Patterns

**Singleton HTTP Client**: The `tools.py` module uses a module-level `_nyt_client` variable to maintain a single NytClient instance across all tool calls. This enables connection pooling and prevents resource leaks. The `get_client()` function lazily initializes this client.

**Rate Limiting Strategy**: Built-in at the NytClient level. The client tracks the timestamp of the last API call and automatically sleeps if insufficient time has passed. Rate limit is configurable via `settings.nyt_rate_limit_seconds` (default 12 seconds = 5 req/min).

**Response Formatting**: Most tools return formatted responses via utils.py formatters to simplify output. Archive and bestseller endpoints return raw API responses for maximum flexibility.

**Parameter Filtering**: The `filter_params()` utility removes None, empty strings, and 0 values from request parameters to keep API calls minimal and avoid sending unnecessary parameters.

## NYT API Details

**Rate Limits**: 5 requests per minute, 500 requests per day (enforced by NytClient)

**Available Tools**:
1. `search_articles` - Article Search API (formatted response)
2. `get_news_wire` - News Wire API (formatted response)
3. `get_most_popular` - Most Popular API (formatted response)
4. `get_archive` - Archive API (raw response)
5. `get_bestseller_list` - Books API (raw response)

**Available Resources**:
1. `nyt://reference/sections` - Valid sections for news wire
2. `nyt://reference/bestseller-lists` - Valid bestseller list names
3. `nyt://reference/api-limits` - Rate limit information

## Important Notes

- Always ensure NYT_API_KEY is set before running the server (validated on startup)
- The server auto-cleans up the HTTP client on shutdown via the main() function
- Date parameters use YYYYMMDD format (e.g., "20231201")
- Archive and bestseller tools return unformatted responses for maximum flexibility

# NYTimes MCP

A FastMCP-based Model Context Protocol (MCP) server that provides access to the New York Times APIs through native MCP tools and resources.

## Overview

This MCP server provides 6 specialized tools for accessing various New York Times APIs:
- **Article Search** - Search the NYT article archive
- **News Wire** - Real-time news feed
- **Most Popular** - Most viewed/shared/emailed articles
- **Archive** - Monthly article archives
- **Bestseller Lists** - NYT book bestseller lists

## Features

- **Native MCP Protocol**: Built with FastMCP for seamless integration with MCP clients
- **5 Specialized Tools**: One tool per NYT API endpoint for maximum flexibility
- **3 Reference Resources**: Discoverable resources for available sections, lists, and API limits
- **Formatted Responses**: Clean, simplified responses for most endpoints
- **Type-Safe Parameters**: Full type validation on all tool parameters
- **Error Handling**: Robust error management with detailed error messages

## Requirements

- Python 3.13+
- NYT API Key (get one at [NYT Developer Portal](https://developer.nytimes.com/))
- uv or pip for package management

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/your-username/nytimes-mcp.git
cd nytimes-mcp
```

### 2. Install with uv (recommended)

```bash
ux tool install .
```

Or with pip:

```bash
pip install -e .
```

### 3. Configure API Key

Ensure you have your NYT API key in your environment.

```bash
export NYT_API_KEY=your_api_key_here
```

Alternatively, create a `.env` file:

```env
NYT_API_KEY=your_api_key_here
```

### 4. Run the Server

#### Development Mode (with Inspector)

```bash
fastmcp dev src/nytimes_mcp/server.py:mcp
```

This starts the MCP Inspector UI for testing tools interactively.

#### Production Mode

```bash
uvx nytimes-mcp
```

Or use the FastMCP run command:

```bash
fastmcp run src/nytimes_mcp/server.py:mcp
```

## Project Structure

```
nytimes-mcp/
├── src/
│   └── nytimes_mcp/
│       ├── __init__.py
│       ├── server.py         # FastMCP server with tool/resource definitions
│       ├── tools.py           # NYT API tool implementations
│       ├── resources.py       # MCP resource definitions
│       ├── nyt_client.py      # NYT API client logic
│       ├── utils.py           # Response formatting utilities
│       └── config.py          # Configuration settings
├── .env
├── .gitignore
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

## Available MCP Tools

### 1. search_articles
Search NYT articles by query, date range, and other criteria.

**Parameters:**
- `query` (string, required): Search query
- `sort` (string, optional): "newest" or "oldest" (default: "newest")
- `begin_date` (string, optional): Start date in YYYYMMDD format
- `end_date` (string, optional): End date in YYYYMMDD format
- `page` (int, optional): Page number for pagination

**Returns:** Formatted response with articles array containing headline, snippet, web_url, and pub_date

### 2. get_latest_news
Get the latest news items from the NYT news wire.

**Parameters:**
- `limit` (int, optional): Number of items to return (default: 20)
- `offset` (int, optional): Pagination offset (default: 0)
- `source` (string, optional): "nyt" or "inyt" (default: "nyt")
- `section` (string, optional): relevant section, e.g. "u.s.", "technology" (default: "all")
  - See `nyt://reference/sections` resource for available sections

**Returns:** Formatted response with news_items array

### 3. get_most_popular
Get the most popular NYT articles.

**Parameters:**
- `type` (string, optional): "viewed", "shared", or "emailed" (default: "viewed")
- `time_period` (string, optional): "1", "7", or "30" days (default: "1")
  - See `nyt://reference/popular-types` resource for available options

**Returns:** Formatted response with articles array

### 4. get_archive
Get NYT articles from a specific month and year archive.

**Parameters:**
- `year` (int, optional): Year (default: current year)
- `month` (int, optional): Month 1-12 (default: current month)

**Returns:** Full NYT archive API response (unformatted)

### 5. get_bestseller_list
Get NYT bestseller lists.

**Parameters:**
- `list` (string, optional): List name (default: "hardcover-fiction")
  - See `nyt://reference/bestseller-lists` resource for available list names
- `offset` (int, optional): Pagination offset (default: 0)

**Returns:** Full NYT Books API response (unformatted)

## Available MCP Resources

Resources provide reference data that can be accessed by MCP clients:

- `nyt://reference/sections` - Available sections for top_stories
- `nyt://reference/bestseller-lists` - Available bestseller list names
- `nyt://reference/api-limits` - NYT API rate limits and usage information

## Using with MCP Clients

### Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "nytimes": {
      "command": "uvx",
      "args": ["nytimes-mcp"],
      "env": {
        "NYT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Development

### Install Development Dependencies

```bash
uv sync
```

### Run Tests

```bash
uv run pytest
```

### Development Server with Inspector

```bash
uv run fastmcp dev src/nytimes_mcp/server.py:mcp
```

This opens the MCP Inspector for interactive testing.

## API Rate Limits

The NYT API has rate limits (approximately 5 requests/minute, 500 requests/day maximum). Use the `nyt://reference/api-limits` resource to check current limits.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License

## Security Note

- Never commit your `.env` file
- Keep your NYT API key private
- Use environment variables for sensitive data

## Contact

Create an issue for bug reports or feature requests.

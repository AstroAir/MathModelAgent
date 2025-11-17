# Web Search Integration for MathModelAgent

This module provides comprehensive web search capabilities for the MathModelAgent project, supporting multiple search providers with fallback mechanisms and robust error handling.

## Features

- **Multiple Search Providers**: Support for Tavily and Exa APIs
- **Extensible Architecture**: Easy to add new search providers
- **Fallback Mechanisms**: Automatic failover between providers
- **Rate Limiting**: Built-in rate limiting to respect API limits
- **Error Handling**: Comprehensive error handling and graceful degradation
- **Search Types**: Support for different search types (general, academic, code, news, research)
- **Content Retrieval**: Get full content from URLs (Exa provider)
- **Similar Search**: Find similar pages to a given URL (Exa provider)

## Configuration

Add the following environment variables to your `.env` file:

```bash
# Search Provider API Keys
TAVILY_API_KEY=tvly-your-api-key-here
EXA_API_KEY=your-exa-api-key-here

# Search Configuration
SEARCH_DEFAULT_PROVIDER=tavily
SEARCH_MAX_RESULTS=10
SEARCH_TIMEOUT=30
SEARCH_ENABLE_FALLBACK=true
SEARCH_FALLBACK_PROVIDERS=exa
```

## Usage Examples

### Basic Web Search

```python
from app.tools.web_search_tool import WebSearchTool

# Initialize the tool
search_tool = WebSearchTool()

# Perform a basic search
result = await search_tool.search(
    query="latest machine learning techniques",
    search_type="academic",
    max_results=5
)

if result.error:
    print(f"Search failed: {result.error}")
else:
    print(f"Search results: {result.result}")
```

### Using Search Manager Directly

```python
from app.tools.search.search_manager import search_manager
from app.schemas.search import SearchRequest, SearchType, SearchProvider

# Create a search request
request = SearchRequest(
    query="Python mathematical modeling libraries",
    search_type=SearchType.CODE,
    provider=SearchProvider.TAVILY,
    max_results=8
)

# Perform the search
response = await search_manager.search(request)

# Process results
for result in response.results:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Content: {result.content[:200]}...")
    print("---")
```

### Agent Integration

The web search functionality is automatically available to agents through the tool system:

```python
# In WriterAgent or CoderAgent, the LLM can call:
{
    "name": "web_search",
    "arguments": {
        "query": "latest research on neural networks",
        "search_type": "academic",
        "provider": "exa",
        "max_results": 5
    }
}
```

## Search Types

- **general**: General web search (default)
- **academic**: Academic papers and research
- **code**: Code examples and documentation
- **news**: News articles and current events
- **research**: In-depth research with summaries

## Provider Comparison

| Feature | Tavily | Exa |
|---------|--------|-----|
| General Search | ✅ | ✅ |
| Academic Search | ✅ | ✅ |
| Code Search | ✅ | ✅ |
| Content Extraction | ✅ | ✅ |
| Similar Page Search | ❌ | ✅ |
| Answer Generation | ✅ | ❌ |
| Follow-up Questions | ✅ | ❌ |

## Error Handling

The system includes comprehensive error handling:

- **Rate Limiting**: Automatic rate limiting with configurable limits
- **Fallback Providers**: Automatic failover to backup providers
- **Timeout Handling**: Configurable request timeouts
- **Authentication Errors**: Clear error messages for API key issues
- **Network Errors**: Graceful handling of network connectivity issues

## Rate Limiting

Rate limiting is automatically applied based on provider configurations:

```python
# Set custom rate limits
from app.tools.search.rate_limiter import rate_limiter

rate_limiter.set_limit("tavily", 60)  # 60 requests per minute
rate_limiter.set_limit("exa", 100)   # 100 requests per minute
```

## Monitoring and Status

Check provider status and health:

```python
# Get status of all providers
statuses = await search_manager.get_provider_status()

for provider, status in statuses.items():
    print(f"{provider}: Available={status.available}, "
          f"Configured={status.configured}")

# Get status of specific provider
tavily_status = await search_manager.get_provider_status(SearchProvider.TAVILY)
```

## Advanced Features

### Content Retrieval

```python
# Get full content for specific URLs (Exa only)
urls = ["https://example.com/article1", "https://example.com/article2"]
content_map = await search_manager.get_content(urls)

for url, content in content_map.items():
    print(f"Content from {url}: {content[:500]}...")
```

### Similar Page Search

```python
# Find similar pages (Exa only)
similar_results = await search_manager.find_similar(
    url="https://example.com/reference-article",
    num_results=10
)

for result in similar_results:
    print(f"Similar: {result.title} - {result.url}")
```

## Testing

Run the test suite to validate functionality:

```bash
# Run all search tests
pytest backend/app/tests/test_search_functionality.py -v

# Run specific test categories
pytest backend/app/tests/test_search_functionality.py::TestSearchProviders -v
pytest backend/app/tests/test_search_functionality.py::TestSearchManager -v
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure API keys are correctly set in environment variables
2. **Rate Limiting**: Check rate limit status and wait for reset if needed
3. **Network Timeouts**: Increase timeout values in configuration
4. **Provider Unavailable**: Enable fallback providers for redundancy

### Debug Logging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.getLogger('app.tools.search').setLevel(logging.DEBUG)
```

## Contributing

To add a new search provider:

1. Create a new provider class inheriting from `BaseSearchProvider`
2. Implement required abstract methods
3. Add provider configuration to settings
4. Update the search manager to initialize the new provider
5. Add comprehensive tests

## License

This search integration is part of the MathModelAgent project and follows the same licensing terms.

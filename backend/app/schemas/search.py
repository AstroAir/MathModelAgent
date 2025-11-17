from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SearchProvider(str, Enum):
    """Supported search providers"""

    TAVILY = "tavily"
    EXA = "exa"


class SearchType(str, Enum):
    """Types of search queries"""

    GENERAL = "general"
    ACADEMIC = "academic"
    CODE = "code"
    NEWS = "news"
    RESEARCH = "research"


class SearchResult(BaseModel):
    """Individual search result"""

    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the search result")
    content: Optional[str] = Field(None, description="Content/snippet from the result")
    score: Optional[float] = Field(None, description="Relevance score")
    published_date: Optional[datetime] = Field(
        None, description="Publication date if available"
    )
    source: Optional[str] = Field(None, description="Source domain or publication")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class SearchRequest(BaseModel):
    """Search request parameters"""

    query: str = Field(..., description="Search query string")
    provider: Optional[SearchProvider] = Field(
        None, description="Preferred search provider"
    )
    search_type: SearchType = Field(SearchType.GENERAL, description="Type of search")
    max_results: Optional[int] = Field(None, description="Maximum number of results")
    include_content: bool = Field(True, description="Whether to include full content")
    domains: Optional[List[str]] = Field(None, description="Specific domains to search")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range filter")
    language: Optional[str] = Field("en", description="Search language")


class SearchResponse(BaseModel):
    """Search response containing results and metadata"""

    results: List[SearchResult] = Field(
        default_factory=list, description="Search results"
    )
    query: str = Field(..., description="Original search query")
    provider: SearchProvider = Field(..., description="Provider used for search")
    total_results: Optional[int] = Field(
        None, description="Total number of results available"
    )
    search_time: float = Field(..., description="Time taken for search in seconds")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional response metadata"
    )


class SearchConfig(BaseModel):
    """Configuration for search providers"""

    provider: SearchProvider = Field(..., description="Search provider name")
    api_key: str = Field(..., description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Custom base URL if needed")
    timeout: int = Field(30, description="Request timeout in seconds")
    max_results: int = Field(10, description="Default maximum results")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")
    custom_params: Dict[str, Any] = Field(
        default_factory=dict, description="Provider-specific parameters"
    )


class SearchError(Exception):
    """Custom exception for search-related errors"""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        super().__init__(self.message)


class SearchProviderStatus(BaseModel):
    """Status information for a search provider"""

    provider: SearchProvider = Field(..., description="Provider name")
    available: bool = Field(..., description="Whether provider is available")
    configured: bool = Field(..., description="Whether provider is properly configured")
    last_error: Optional[str] = Field(None, description="Last error message if any")
    rate_limit_remaining: Optional[int] = Field(
        None, description="Remaining rate limit"
    )
    response_time: Optional[float] = Field(None, description="Average response time")

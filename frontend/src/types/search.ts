// Search-related types for frontend
export interface SearchResultMetadata {
	highlights?: string[];
	[key: string]: unknown;
}

export interface SearchResult {
	title: string;
	url: string;
	content?: string;
	score?: number;
	published_date?: string;
	source?: string;
	metadata?: SearchResultMetadata;
}

export interface SearchResponse {
	results: SearchResult[];
	query: string;
	provider: SearchProvider;
	total_results?: number;
	search_time: number;
	metadata?: Record<string, unknown>;
}

export interface SearchDateRange {
	start_date?: string;
	end_date?: string;
}

export interface SearchRequest {
	query: string;
	provider?: SearchProvider;
	search_type?: SearchType;
	max_results?: number;
	include_content?: boolean;
	domains?: string[];
	date_range?: SearchDateRange;
	language?: string;
}

export enum SearchProvider {
	TAVILY = "tavily",
	EXA = "exa",
}

export enum SearchType {
	GENERAL = "general",
	ACADEMIC = "academic",
	CODE = "code",
	NEWS = "news",
	RESEARCH = "research",
}

export interface SearchConfig {
	provider: SearchProvider;
	api_key: string;
	base_url?: string;
	timeout: number;
	max_results: number;
	rate_limit?: number;
	custom_params?: Record<string, unknown>;
}

export interface SearchProviderStatus {
	provider: SearchProvider;
	available: boolean;
	configured: boolean;
	last_error?: string;
	rate_limit_remaining?: number;
	response_time?: number;
}

export interface SearchError {
	message: string;
	provider?: string;
	error_code?: string;
}

export interface SearchSettings {
	default_provider: SearchProvider;
	max_results: number;
	timeout: number;
	enable_fallback: boolean;
	fallback_providers: SearchProvider[];
}

// UI-specific types
export interface SearchFormData {
	query: string;
	searchType: SearchType;
	provider?: SearchProvider;
	maxResults: number;
}

export interface SearchState {
	isLoading: boolean;
	results: SearchResult[];
	error: string | null;
	lastQuery: string;
	searchTime: number;
	totalResults: number;
}

import type {
	SearchProvider,
	SearchProviderStatus,
	SearchRequest,
	SearchResponse,
	SearchSettings,
} from "@/types/search";
import request from "@/utils/request";

/**
 * Perform a web search using the configured providers
 */
export function performWebSearch(searchRequest: SearchRequest) {
	return request.post<SearchResponse>("/search/web", searchRequest);
}

/**
 * Get content for specific URLs (Exa provider only)
 */
export function getWebContent(urls: string[]) {
	return request.post<Record<string, string>>("/search/content", { urls });
}

/**
 * Find similar pages to a given URL (Exa provider only)
 */
export function findSimilarPages(url: string, numResults = 10) {
	return request.post<SearchResponse>("/search/similar", {
		url,
		num_results: numResults,
	});
}

/**
 * Get status of search providers
 */
export function getSearchProviderStatus(provider?: SearchProvider) {
	const params = provider ? { provider } : {};
	return request.get<
		Record<string, SearchProviderStatus> | SearchProviderStatus
	>("/search/status", { params });
}

/**
 * Get available search providers
 */
export function getAvailableProviders() {
	return request.get<SearchProvider[]>("/search/providers");
}

/**
 * Get search settings/configuration
 */
export function getSearchSettings() {
	return request.get<SearchSettings>("/search/settings");
}

/**
 * Update search settings
 */
export function updateSearchSettings(settings: Partial<SearchSettings>) {
	return request.put<SearchSettings>("/search/settings", settings);
}

/**
 * Test search provider connectivity
 */
export function testSearchProvider(provider: SearchProvider) {
	return request.post<{
		success: boolean;
		message: string;
		response_time?: number;
	}>("/search/test", { provider });
}

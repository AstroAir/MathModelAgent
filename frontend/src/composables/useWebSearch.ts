import {
	findSimilarPages,
	getAvailableProviders,
	getSearchProviderStatus,
	getWebContent,
	performWebSearch,
} from "@/apis/searchApi";
import type {
	SearchProvider,
	SearchProviderStatus,
	SearchRequest,
	SearchResult,
	SearchState,
} from "@/types/search";
import { SearchType } from "@/types/search";
import { computed, reactive, ref } from "vue";

export function useWebSearch() {
	// Reactive state
	const searchState = reactive<SearchState>({
		isLoading: false,
		results: [],
		error: null,
		lastQuery: "",
		searchTime: 0,
		totalResults: 0,
	});

	const availableProviders = ref<SearchProvider[]>([]);
	const providerStatuses = ref<Record<string, SearchProviderStatus>>({});

	// Computed properties
	const hasResults = computed(() => searchState.results.length > 0);
	const hasError = computed(() => !!searchState.error);
	const isSearching = computed(() => searchState.isLoading);

	// Methods
	const performSearch = async (
		searchRequest: SearchRequest,
	): Promise<SearchResult[]> => {
		searchState.isLoading = true;
		searchState.error = null;
		searchState.results = [];

		try {
			const response = await performWebSearch(searchRequest);

			searchState.results = response.data.results;
			searchState.lastQuery = searchRequest.query;
			searchState.searchTime = response.data.search_time;
			searchState.totalResults =
				response.data.total_results || response.data.results.length;

			return searchState.results;
		} catch (error: unknown) {
			const apiError = error as {
				response?: {
					data?: {
						detail?: { message?: string };
						message?: string;
					};
				};
				message?: string;
			};
			const errorMessage =
				apiError.response?.data?.detail?.message ||
				apiError.response?.data?.message ||
				apiError.message ||
				"Search failed";
			searchState.error = errorMessage;
			throw new Error(errorMessage);
		} finally {
			searchState.isLoading = false;
		}
	};

	const getContentForUrl = async (url: string): Promise<string | null> => {
		try {
			const response = await getWebContent([url]);
			return response.data[url] || null;
		} catch (error: unknown) {
			console.error("Failed to get content for URL:", error);
			return null;
		}
	};

	const getContentForUrls = async (
		urls: string[],
	): Promise<Record<string, string>> => {
		try {
			const response = await getWebContent(urls);
			return response.data;
		} catch (error: unknown) {
			console.error("Failed to get content for URLs:", error);
			return {};
		}
	};

	const findSimilar = async (
		url: string,
		numResults = 10,
	): Promise<SearchResult[]> => {
		try {
			const response = await findSimilarPages(url, numResults);
			return response.data.results || [];
		} catch (error: unknown) {
			console.error("Failed to find similar pages:", error);
			const apiError = error as {
				response?: {
					data?: {
						detail?: { message?: string };
					};
				};
			};
			throw new Error(
				apiError.response?.data?.detail?.message ||
					"Failed to find similar pages",
			);
		}
	};

	const loadProviders = async (): Promise<void> => {
		try {
			const response = await getAvailableProviders();
			availableProviders.value = response.data;
		} catch (error: unknown) {
			console.error("Failed to load providers:", error);
		}
	};

	const checkProviderStatus = async (
		provider?: SearchProvider,
	): Promise<void> => {
		try {
			const response = await getSearchProviderStatus(provider);

			if (provider) {
				// Single provider status
				providerStatuses.value[provider] =
					response.data as SearchProviderStatus;
			} else {
				// All providers status
				providerStatuses.value = response.data as Record<
					string,
					SearchProviderStatus
				>;
			}
		} catch (error: unknown) {
			console.error("Failed to check provider status:", error);
		}
	};

	const clearResults = (): void => {
		searchState.results = [];
		searchState.error = null;
		searchState.lastQuery = "";
		searchState.searchTime = 0;
		searchState.totalResults = 0;
	};

	const clearError = (): void => {
		searchState.error = null;
	};

	// Quick search methods for common use cases
	const searchGeneral = async (
		query: string,
		maxResults = 10,
	): Promise<SearchResult[]> => {
		return performSearch({
			query,
			search_type: SearchType.GENERAL,
			max_results: maxResults,
			include_content: true,
		});
	};

	const searchAcademic = async (
		query: string,
		maxResults = 10,
	): Promise<SearchResult[]> => {
		return performSearch({
			query,
			search_type: SearchType.ACADEMIC,
			max_results: maxResults,
			include_content: true,
		});
	};

	const searchCode = async (
		query: string,
		maxResults = 10,
	): Promise<SearchResult[]> => {
		return performSearch({
			query,
			search_type: SearchType.CODE,
			max_results: maxResults,
			include_content: true,
		});
	};

	const searchNews = async (
		query: string,
		maxResults = 10,
	): Promise<SearchResult[]> => {
		return performSearch({
			query,
			search_type: SearchType.NEWS,
			max_results: maxResults,
			include_content: true,
		});
	};

	const searchResearch = async (
		query: string,
		maxResults = 10,
	): Promise<SearchResult[]> => {
		return performSearch({
			query,
			search_type: SearchType.RESEARCH,
			max_results: maxResults,
			include_content: true,
		});
	};

	// Utility methods
	const formatSearchResults = (results: SearchResult[]): string => {
		if (!results.length) return "No results found.";

		return results
			.map((result, index) => {
				const content = result.content
					? result.content.length > 200
						? `${result.content.substring(0, 200)}...`
						: result.content
					: "No content preview available.";

				return `${index + 1}. ${result.title}\n   URL: ${result.url}\n   ${content}\n`;
			})
			.join("\n");
	};

	const getResultsByDomain = (domain: string): SearchResult[] => {
		return searchState.results.filter((result) => {
			try {
				return new URL(result.url).hostname.includes(domain);
			} catch {
				return false;
			}
		});
	};

	const getHighScoredResults = (minScore = 0.8): SearchResult[] => {
		return searchState.results.filter(
			(result) => result.score && result.score >= minScore,
		);
	};

	// Initialize providers on composable creation
	loadProviders();

	return {
		// State
		searchState: searchState as Readonly<SearchState>,
		availableProviders: availableProviders.value as Readonly<SearchProvider[]>,
		providerStatuses: providerStatuses.value as Readonly<
			Record<SearchProvider, SearchProviderStatus>
		>,

		// Computed
		hasResults,
		hasError,
		isSearching,

		// Methods
		performSearch,
		getContentForUrl,
		getContentForUrls,
		findSimilar,
		loadProviders,
		checkProviderStatus,
		clearResults,
		clearError,

		// Quick search methods
		searchGeneral,
		searchAcademic,
		searchCode,
		searchNews,
		searchResearch,

		// Utility methods
		formatSearchResults,
		getResultsByDomain,
		getHighScoredResults,
	};
}
